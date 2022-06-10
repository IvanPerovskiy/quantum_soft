from django.shortcuts import render
from django.db.models import F

from main.models import Tree, Cache
from main.utils import sort_result_for_cache, sort_result_for_tree, get_depth


def index(request):
	"""
	Основная страница с формами
	"""

	items = Tree.objects.order_by('id').values('value', 'depth', 'id', 'parent_id', 'is_deleted')
	# Сортируем дерево для правильного вывода
	data = {}
	for item in items:
		if item['depth'] in data:
			data[item['depth']].append(item)
		else:
			data[item['depth']] = [item, ]
	trees = sort_result_for_tree(data, parent_id=None, depth=0, result=None)

	cache = Cache.objects.order_by(F('cache_parent_id').asc(nulls_first=True), 'tree_id').values(
		'value', 'id', 'parent_id', 'is_deleted', 'tree_id', 'cache_parent_id'
	)
	# Сортируем кэш для правильного вывода
	levels = {}
	for item in cache:
		get_depth(item, levels)
	data = {}
	for item in cache:
		if item['depth'] in data:
			data[item['depth']].append(item)
		else:
			data[item['depth']] = [item, ]
	cache = sort_result_for_cache(data, parent_id=None, depth=0, result=None)

	return render(request, "main/base.html", {'trees':trees, 'cache': cache})

