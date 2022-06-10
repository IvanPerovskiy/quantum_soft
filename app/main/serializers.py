from rest_framework import serializers

from main.models import Cache


class CacheSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cache
        fields = ('id', 'value', 'tree_id', 'parent_id')


class CacheUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cache
        fields = ('value', )


class CacheCreateSerializer(serializers.ModelSerializer):
    cache_parent_id = serializers.IntegerField()
    class Meta:
        model = Cache
        fields = ('value', 'cache_parent_id')

    def create(self, validated_data):
        cache_parent = Cache.objects.filter(id=validated_data['cache_parent_id']).first()
        current_item = Cache.objects.create(
            value=validated_data['value'],
            parent_id=cache_parent.tree_id,
            cache_parent_id=cache_parent.id,
            is_new=True
        )
        return current_item


class LoadSerializer(serializers.Serializer):
    tree_id = serializers.IntegerField()











