from django.conf import settings
from django.db import transaction, connection
from django.contrib.auth import get_user_model

from main.models import Tree


TREE_JSON = [
	{
		'value': 'Node1',
		'children':
			[
				{
				'value': 'Node2',
				'children':
					[
						{
							'value': 'Node3',
							'children':
								[
									{
									'value': 'Node4',
									'children': []
									},
									{
									'value': 'Node5',
									'children': []
									},
									{
									'value': 'Node6',
									'children':
										[
											{
											'value': 'Node7',
											'children': []
											}
										]
									}
								]
						},
						{
							'value': 'Node8',
							'children':
								[
									{
										'value': 'Node9',
										'children':
											[
												{
													'value': 'Node10',
													'children': []
												},
												{
													'value': 'Node11',
													'children': []
												},
												{
													'value': 'Node12',
													'children':
														[
															{
																'value': 'Node13',
																'children': []
															}
														]
												}
											]
									}
								]
						}
					]
				}
			]
	}
]


def get_or_create_superuser():
	superuser = get_user_model().objects.filter(
		is_superuser=True
	).first()
	if not superuser:
		get_user_model().objects.create_superuser(
			username=settings.SUPERUSER_NAME,
			password=settings.SUPERUSER_PASSWORD
		)


def create_item_tree(value, parent_id, depth):
	return Tree.objects.create(
		value=value,
		parent_id=parent_id,
		depth=depth
	)


def create_tree(tree_json: list, parent_id=None, depth=0):
	with transaction.atomic():
		for item in tree_json:
			item_db = create_item_tree(item['value'], parent_id=parent_id, depth=depth)
			create_tree(item['children'], parent_id=item_db.id, depth=depth+1)

def get_child_ids(item_id):
	# Выбирает идентификаторы всех потомков
	query = f"""
	with recursive r as (
    select
		id, parent_id, value
		from main_tree
		where parent_id = {item_id}
  	union
    select
		st.id, st.parent_id, st.value
		from main_tree as st
		join r
		on st.parent_id = r.id
	)
	select id from r;
	"""
	with connection.cursor() as cursor:
		cursor.execute(query)
		ids = cursor.fetchall()
		return [id[0] for id in ids]

def start_service():
	"""
    Вызывается при сборке проекта. Если не было создано дерево, заполняется таблица
    """
	get_or_create_superuser()
	if len(Tree.objects.all()) == 0:
		create_tree(TREE_JSON)


