from django.contrib import admin
from main.models import *


class TreeAdmin(admin.ModelAdmin):
    model = Tree


class CacheAdmin(admin.ModelAdmin):
    model = Cache


admin.site.register(Cache, CacheAdmin)
admin.site.register(Tree, TreeAdmin)
