from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from main.models import Cache, Tree
from main.responses import *
from main.utils import create_tree, TREE_JSON
from main.serializers import CacheSerializer, LoadSerializer, CacheUpdateSerializer, CacheCreateSerializer


class CacheViewSet(viewsets.GenericViewSet):
    queryset = Cache.objects.all()
    serializer_class = CacheSerializer
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        if self.action == 'update':
            return CacheUpdateSerializer
        elif self.action == 'create':
            return CacheCreateSerializer
        return self.serializer_class

    def list(self, request, *args, **kwargs):
        """
        Список всех элементов в кэше
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={
        200: SUCCESS_RESPONSE,
        400: BAD_REQUEST
    })
    @action(
        detail=False,
        methods=['post'],
        permission_classes=(AllowAny,),
        serializer_class=LoadSerializer,
        url_path='load'
    )
    def load(self, request, *args, **kwargs):
        """
        Загрузка одного элемента из базы в кэш
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tree_item = Tree.objects.filter(id=serializer.validated_data['tree_id']).first()
        if not tree_item:
            raise ValidationError('Не найден элемент в базе')
        cache_item = Cache.objects.filter(tree_id=serializer.validated_data['tree_id']).first()
        if cache_item:
            raise ValidationError('Этот элемент уже добавлен. Сохраните изменения')

        is_deleted = tree_item.is_deleted
        if not tree_item.parent_id:
            cache_parent_item = None
        else:
            cache_parent_item = Cache.objects.filter(tree_id=tree_item.parent_id).first()
            if cache_parent_item and cache_parent_item.is_deleted:
                is_deleted = True

        new_cache_item = Cache.objects.create(
            tree_id=tree_item.id,
            cache_parent=cache_parent_item,
            value=tree_item.value,
            parent_id=tree_item.parent_id,
            is_deleted=is_deleted
        )
        Cache.objects.filter(parent_id=new_cache_item.tree_id).update(cache_parent_id=new_cache_item.id)
        if is_deleted:
            # При загрузке удаленного элемента удаляем всех потомков в кэше
            new_cache_item.remove_children_from_cache()
        return Response(status=status.HTTP_200_OK)


    @swagger_auto_schema(responses={
        200: SUCCESS_RESPONSE,
        404: NOT_FOUND,
        400: BAD_REQUEST
    })
    def create(self, request, pk=None):
        """
        Создание нового элемента в кэше
        """
        cache_parent = Cache.objects.filter(id=request.data.get('cache_parent_id')).first()
        if cache_parent and cache_parent.is_deleted:
            return Response('Невозможно создать элемент с удаленным родителем', status=status.HTTP_200_OK)
        serializer = CacheCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)


    @swagger_auto_schema(responses={
        200: SUCCESS_RESPONSE,
        404: NOT_FOUND,
        400: BAD_REQUEST
    })
    def update(self, request, pk=None):
        """
        Редактирование элемента в кэше
        """
        serializer = CacheUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=False)
        instance = self.get_object()
        if instance.is_deleted:
            return Response('Удаленный элемент запрещено редактировать', status=status.HTTP_200_OK)

        instance.set_value(serializer.validated_data['value'])
        return Response(status=status.HTTP_200_OK)


    @swagger_auto_schema(responses={
        200: SUCCESS_RESPONSE,
        404: NOT_FOUND,
        400: BAD_REQUEST
    })
    def destroy(self, request, pk=None):
        """
        Удаление элемента в кэше. Физически не удаляется, только помечается флагом
        """
        instance = self.get_object()
        if instance.is_deleted:
            return Response('Элемент уже удален', status=status.HTTP_200_OK)
        instance.remove()
        return Response(status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={
        200: SUCCESS_RESPONSE,
        400: BAD_REQUEST
    })
    @action(
        detail=False,
        methods=['post'],
        permission_classes=(AllowAny,),
        serializer_class=None,
        url_path='save'
    )
    def save_changes(self, request):
        """
        Сохранить изменения в базу
        """
        change_items = Cache.objects.filter(is_sent=False)
        change_dict = {
            item['tree_id']: {'value': item['value'], 'is_deleted': item['is_deleted']}
            for item in change_items.filter(is_new=False).values('tree_id', 'value', 'is_deleted')
        }
        new_items = change_items.filter(is_new=True).order_by('id')
        try:
            # Добавляем новые элементы
            for item in new_items:
                if item.parent_id:
                    parent = Tree.objects.get(id=item.parent_id)
                else:
                    parent = Tree.objects.get(id=item.cache_parent.tree_id)

                new_tree_item = Tree.objects.create(
                    parent_id=parent.id,
                    value=item.value,
                    is_deleted=item.is_deleted,
                    depth=parent.depth + 1
                )
                item.tree_id = new_tree_item.id
                item.save()
            # Обновляем старые элементы
            tree_items = Tree.objects.filter(id__in=change_items.filter(is_new=False).values_list('tree_id', flat=True))
            with transaction.atomic():
                for tree_item in tree_items:
                    tree_item.refresh_from_db()
                    tree_item.value = change_dict[tree_item.id]['value']
                    tree_item.save()
                    if not tree_item.is_deleted and change_dict[tree_item.id]['is_deleted']:
                        tree_item.remove()
                    change_dict.pop(tree_item.id)

            change_items.update(is_sent=True, is_new=False)
            return Response(status=status.HTTP_200_OK)
        except ConnectionError:
            """
            Эмулируем обрыв связи с деревом. Так как вся загрузка у нас происходит одной транзакцией,
            данные не потеряются. И как только связь восстановится все данные передадутся. 
            """
            return Response(status=status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(responses={
        200: SUCCESS_RESPONSE,
        400: BAD_REQUEST
    })
    @action(
        detail=False,
        methods=['post'],
        permission_classes=(AllowAny,),
        serializer_class=None,
        url_path='clear'
    )
    def clear_cache(self, request):
        """
        Очистить кэш
        """
        Cache.objects.all().delete()
        return Response(status=status.HTTP_200_OK)


    @swagger_auto_schema(responses={
        200: SUCCESS_RESPONSE,
        400: BAD_REQUEST
    })
    @action(
        detail=False,
        methods=['post'],
        permission_classes=(AllowAny,),
        serializer_class=None,
        url_path='reset'
    )
    def reset(self, request):
        """
        Вернуть приложение в начальное состояние
        """
        Cache.objects.all().delete()
        Tree.objects.all().delete()
        create_tree(TREE_JSON)
        return Response(status=status.HTTP_200_OK)





