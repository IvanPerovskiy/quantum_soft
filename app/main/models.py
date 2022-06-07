from datetime import datetime
from django.db import models


class Tree(models.Model):
    value = models.CharField(max_length=200)
    parent = models.ForeignKey('Tree', on_delete=models.CASCADE, null=True, blank=True)
    depth = models.BigIntegerField()

    created = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    updated = models.DateTimeField(default=datetime.now)


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
        self.is_deleted = True
        self.is_sent = False
        self.save()