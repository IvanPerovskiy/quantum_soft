from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from main.utils import create_tree, TREE_JSON
from main.models import Cache, Tree


class ApiTestCase(TestCase):
    def setUp(self):
        create_tree(TREE_JSON)
        self.client = APIClient()

    def load_item(self, item_id):
        response = self.client.post('/api/load', {
            'tree_id': item_id
        }, format='json')
        if response.status_code == 400:
            print(response.data)
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/')
        self.assertEqual(tuple(list(response.context)[0].keys()), ('trees', 'cache'))
        self.assertEqual(response.status_code, 200)

    def make_cache(self):
        for i in range(1,10):
            self.load_item(i)
        self.assertEqual(len(Cache.objects.all()), 9)
        self.current_node = Cache.objects.get(tree_id=5)

    def change_node(self):
        response = self.client.put(f'/api/{self.current_node.id}', {
            'value': 'New_node'
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.current_node.refresh_from_db()
        self.assertEqual(self.current_node.value, 'New_node')

        response = self.client.delete(f'/api/{self.current_node.id}')
        self.assertEqual(response.status_code, 200)
        self.current_node.refresh_from_db()
        self.assertEqual(self.current_node.is_deleted, True)

        response = self.client.put(f'/api/{self.current_node.id}', {
            'value': 'New_delete_node'
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, 'Удаленный элемент запрещено редактировать')
        self.current_node.refresh_from_db()
        self.assertEqual(self.current_node.value, 'New_node')

    def test_cache(self):
        self.make_cache()
        self.assertEqual(self.current_node.value, 'Node5')
        self.change_node()

        response = self.client.post(f'/api/clear')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(Cache.objects.all()), 0)

        self.make_cache()
        self.assertEqual(self.current_node.value, 'Node5')
        self.change_node()
        response = self.client.post(f'/api/save')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(Cache.objects.all()), 9)

        tree_node = Tree.objects.get(id=self.current_node.tree_id)
        self.assertEqual(tree_node.value, 'New_node')
        self.assertEqual(tree_node.is_deleted, True)




