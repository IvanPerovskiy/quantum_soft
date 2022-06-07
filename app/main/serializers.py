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


class LoadSerializer(serializers.Serializer):
    tree_id = serializers.IntegerField()











