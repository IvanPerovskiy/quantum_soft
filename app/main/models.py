from datetime import datetime
from django.db import models, transaction


class Tree(models.Model):
    value = models.CharField(max_length=200)
    parent = models.ForeignKey('Tree', on_delete=models.CASCADE, null=True, blank=True)
    depth = models.BigIntegerField()

    created = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    updated = models.DateTimeField(default=datetime.now)

    def remove(self):
        with transaction.atomic():
            self.is_deleted = True
            self.save()
            self.remove_children_from_tree()

    def remove_children_from_tree(self):
        from main.utils import get_child_ids
        childs_ids = get_child_ids(self.id)
        Tree.objects.filter(id__in=childs_ids).update(is_deleted=True)


class Cache(models.Model):
    tree_id = models.BigIntegerField(db_index=True)
    parent_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    value = models.CharField(max_length=200)

    created = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)

    def set_value(self, value):
        self.value = value
        self.is_sent = False
        self.save()

    def remove(self):
        with transaction.atomic():
            self.is_deleted = True
            self.is_sent = False
            self.save()
            self.remove_children_from_cache()

    def remove_children_from_cache(self):
        from main.utils import get_child_ids
        childs_ids = get_child_ids(self.tree_id)
        cache_ids = Cache.objects.values_list('tree_id', flat=True)
        Cache.objects.filter(
            parent_id__in=cache_ids,
            tree_id__in=childs_ids,
        ).update(is_deleted=True)
