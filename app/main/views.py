from django.shortcuts import render

from main.models import Tree, Cache


def index(request):
	trees = Tree.objects.order_by('id').values('value', 'depth', 'id', 'parent_id', 'is_deleted')
	for item in trees:
		item['value'] = '_'*item['depth'] + item['value']
		if item['is_deleted']:
			item['color'] = 'red'
		else:
			item['color'] = 'black'
	cache = Cache.objects.order_by('tree_id').values('value', 'id', 'parent_id', 'is_deleted', 'tree_id')
	levels = {}
	for item in cache:
		if not item['parent_id']:
			item['depth'] = 0
			levels[item['tree_id']] = 0
		else:
			parent = Cache.objects.filter(tree_id=item['parent_id']).first()
			if not parent:
				item['depth'] = 0
				levels[item['tree_id']] = 0
			else:
				item['depth'] = levels[parent.tree_id] + 1
				levels[item['tree_id']] = item['depth']

		item['value'] = '_'*item['depth'] + item['value']
		if item['is_deleted']:
			item['color'] = 'red'
		else:
			item['color'] = 'black'
	return render(request, "main/base.html", {'trees':trees, 'cache': cache})

