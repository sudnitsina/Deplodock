from django.test import TestCase
from django.urls import reverse

from api.models import *

TOKEN = "790cb216be621e8b2e7c064e21f9f4fb020808071176655f9df1ac713f643d21"
INVENTORY = '{"test_gr": {"vars": {"test_var": "test"}, "hosts": ["test.test"], "children": ["child_gr"]}, "child_gr": {"vars": {}, "hosts": [], "children": []}, "all": {"vars": {"inventory_name": "test_inv"}, "hosts": [], "children": []}}'
INVENTORY2 = '{"test_gr": {"vars": {"test_var": "test"}, "hosts": ["test.test"], "children": ["child_gr"]}, "child_gr": {"vars": {}, "hosts": [], "children": []}, "all": {"vars": {"inventory_name": "upl_inv2"}, "hosts": [], "children": []}, "_meta": {"hostvars":{"test.test":{"test_hostvar": "test"}}}}'


class NotFoundTest(TestCase):
    fixtures = ["tests/api/test_inventory.json"]

    def test_not_api(self):
        url = "/n/a"
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_api_get(self):
        url = "/api/n/a"
        response = self.client.get(url, **{"HTTP_X_AUTH_TOKEN": TOKEN})
        self.assertEquals(response.status_code, 404)
        self.assertEqual(response.content.decode(), '{"detail":"Not found."}')

    def test_api_put(self):
        url = "/api/n/a"
        response = self.client.put(url, **{"HTTP_X_AUTH_TOKEN": TOKEN})
        self.assertEquals(response.status_code, 400)
        self.assertEqual(response.content.decode(), '{"detail":"bad request"}')

class InventoryTest(TestCase):
    fixtures = ["tests/api/test_inventory.json"]

    def test_list(self):
        url = reverse("inventory_list")
        response = self.client.get(url, **{"HTTP_X_AUTH_TOKEN": TOKEN})
        self.assertEquals(response.content.decode(), '["test_inv"]')

    def test_json(self):
        url = reverse("inventory_details", args=["test_inv"])
        response = self.client.get(url, **{"HTTP_X_AUTH_TOKEN": TOKEN})
        self.assertJSONEqual(response.content.decode(), INVENTORY)

    def test_create(self):
        url = reverse("inventory_details", args=["created_inv"])
        response = self.client.put(url, **{"HTTP_X_AUTH_TOKEN": TOKEN})
        self.assertEquals(response.status_code, 200)
        self.assertJSONEqual(response.content.decode(), '{"status":"ADD","details":"inventory"}')
        self.assertTrue(Inventory.objects.filter(inventory="created_inv").exists())

    def test_create_error(self):
        url = reverse("inventory_details", args=["test_inv"])
        response = self.client.put(url, **{"HTTP_X_AUTH_TOKEN": TOKEN})
        self.assertEquals(response.status_code, 200)
        self.assertEqual(response.content.decode(), '"already exists"')

    def test_delete(self):
        url = reverse("inventory_details", args=["test_inv"])
        response = self.client.delete(url, **{"HTTP_X_AUTH_TOKEN": TOKEN})
        self.assertEquals(response.status_code, 200)
        self.assertJSONEqual(response.content.decode(), '{"status":"DELETE","details":"inventory"}')
        self.assertFalse(Inventory.objects.filter(inventory="test_inv").exists())

    def test_upload(self):
        url = reverse('inventory_details', args=["upl_inv2"])
        self.client.delete(url, **{"HTTP_X_AUTH_TOKEN": TOKEN})
        response = self.client.put(url, data=INVENTORY2, **{'HTTP_X_AUTH_TOKEN': TOKEN})
        self.assertEqual(response.content.decode(), 'done')
        url = reverse("inventory_details", args=["upl_inv2"])
        response = self.client.get(url, **{"HTTP_X_AUTH_TOKEN": TOKEN})
        self.assertJSONEqual(response.content.decode(), INVENTORY2)

    def test_upload_error(self):
        url = reverse('inventory_details', args=["upl_inv1"])
        response = self.client.put(url, data='string', **{'HTTP_X_AUTH_TOKEN': TOKEN})
        self.assertEquals(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'invalid data')
        data = '{"test_gr": {"hosts": "string"}}'
        response = self.client.put(url, data=data, **{'HTTP_X_AUTH_TOKEN': TOKEN})
        self.assertEquals(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'hosts should be list')


class GroupTest(TestCase):
    fixtures = ["tests/api/test_inventory.json"]

    def test_list(self):
        url = reverse("group_list", args=["test_inv"])
        response = self.client.get(url, **{"HTTP_X_AUTH_TOKEN": TOKEN})
        self.assertEquals(response.content.decode(), '["child_gr", "test_gr"]')

    def test_create(self):
        url = reverse("group_details", args=["test_inv", "created_group"])
        response = self.client.put(url, **{"HTTP_X_AUTH_TOKEN": TOKEN})
        self.assertEquals(response.status_code, 200)
        self.assertJSONEqual(response.content.decode(), '{"status":"ADD","details":"group"}')
        self.assertTrue(Group.objects.filter(group="created_group").exists())

    def test_create_error(self):
        url = reverse("group_details", args=["test_inv", "test_gr"])
        response = self.client.put(url, **{"HTTP_X_AUTH_TOKEN": TOKEN})
        self.assertEquals(response.status_code, 200)
        self.assertEqual(response.content.decode(), '"already exists"')

    def test_delete(self):
        url = reverse("group_details", args=["test_inv", "test_gr"])
        response = self.client.delete(url, **{"HTTP_X_AUTH_TOKEN": TOKEN})
        self.assertEquals(response.status_code, 200)
        self.assertJSONEqual(response.content.decode(), '{"status":"DELETE","details":"group"}')
        self.assertFalse(Group.objects.filter(group="test_gr").exists())

    def test_delete_error(self):
        url = reverse("group_details", args=["test_inv", "not_exist"])
        response = self.client.delete(url, **{"HTTP_X_AUTH_TOKEN": TOKEN})
        self.assertEquals(response.status_code, 404)
        self.assertEqual(response.content.decode(), '{"detail":"Not found."}')


class MachineTest(TestCase):
    fixtures = ["tests/api/test_inventory.json"]

    def test_list(self):
        url = reverse('machine')
        response = self.client.get(url, **{'HTTP_X_AUTH_TOKEN': TOKEN})
        self.assertEqual(response.content.decode(), '["test.test"]')

    def test_create(self):
        url = reverse('machine', args=['create.test'])
        response = self.client.put(url, **{'HTTP_X_AUTH_TOKEN': TOKEN})
        self.assertEquals(response.status_code, 200)
        self.assertJSONEqual(response.content.decode(), '{"status":"ADD","details":"machine"}')
        self.assertTrue(Machine.objects.filter(machine="create.test").exists())

    def test_create_error(self):
        url = reverse('machine', args=['test.test'])
        response = self.client.put(url, **{'HTTP_X_AUTH_TOKEN': TOKEN})
        self.assertEquals(response.status_code, 200)
        self.assertEqual(response.content.decode(), '"already exists"')

    def test_delete(self):
        url = reverse('machine', args=['test.test'])
        response = self.client.delete(url, **{'HTTP_X_AUTH_TOKEN': TOKEN})
        self.assertEquals(response.status_code, 200)
        self.assertJSONEqual(response.content.decode(), '{"status":"DELETE","details":"machine"}')
        self.assertFalse(Machine.objects.filter(machine="create.test").exists())

    def test_delete_error(self):
        url = reverse('machine', args=['not_exist.test'])
        response = self.client.delete(url, **{'HTTP_X_AUTH_TOKEN': TOKEN})
        self.assertEquals(response.status_code, 404)
        self.assertEqual(response.content.decode(), '{"detail":"Not found."}')


class HostTest(TestCase):
    fixtures = ["tests/api/test_inventory.json"]

    def test_list(self):
        url = reverse('host', args=['test_inv', 'test_gr'])
        response = self.client.get(url, **{'HTTP_X_AUTH_TOKEN': TOKEN})
        self.assertEquals(response.status_code, 200)
        self.assertEqual(response.content.decode(), '["test.test"]')

    def test_create(self):
        url = reverse('host', args=['test_inv', 'child_gr', 'test.test'])
        response = self.client.put(url, **{'HTTP_X_AUTH_TOKEN': TOKEN})
        self.assertEquals(response.status_code, 200)
        self.assertJSONEqual(response.content.decode(), '{"status":"ADD","details":"host"}')
        self.assertTrue(Host.objects.filter(host=Machine.objects.get(machine="test.test"),
                                            group=Group.objects.filter(group="child_gr").exists()))

    def test_create_error(self):
        url = reverse('host', args=['test_inv', 'child_gr', 'not_exist.test'])
        response = self.client.put(url, **{'HTTP_X_AUTH_TOKEN': TOKEN})
        self.assertEquals(response.status_code, 404)
        self.assertJSONEqual(response.content.decode(), '{"detail":"Not found."}')

        url = reverse('host', args=['test_inv', 'test_gr', 'test.test'])
        response = self.client.put(url, **{'HTTP_X_AUTH_TOKEN': TOKEN})
        self.assertEquals(response.status_code, 200)
        self.assertEqual(response.content.decode(), '"already exists"')

    def test_delete(self):
        url = reverse('host', args=['test_inv', 'test_gr', 'test.test'])
        response = self.client.delete(url, **{'HTTP_X_AUTH_TOKEN': TOKEN})
        self.assertEquals(response.status_code, 200)
        self.assertJSONEqual(response.content.decode(), '{"status":"DELETE","details":"host"}')
        self.assertFalse(Host.objects.filter(host=Machine.objects.get(machine="test.test"),
                                             group=Group.objects.filter(group="child_gr").exists()))


class ChildTest(TestCase):
    fixtures = ["tests/api/test_inventory.json"]

    def test_list(self):
        url = reverse('child', args=['test_inv', 'test_gr'])
        response = self.client.get(url, **{'HTTP_X_AUTH_TOKEN': TOKEN})
        self.assertEquals(response.status_code, 200)
        self.assertEqual(response.content.decode(), '["child_gr"]')

    def test_create(self):
        url = reverse('child', args=['test_inv', 'child_gr', 'test_gr'])
        response = self.client.put(url, **{'HTTP_X_AUTH_TOKEN': TOKEN})
        self.assertEquals(response.status_code, 200)
        self.assertJSONEqual(response.content.decode(), '{"status":"ADD","details":"child"}')
        self.assertTrue(Host.objects.filter(host=Machine.objects.get(machine="test.test"),
                                            group=Group.objects.filter(group="child_gr").exists()))

    def test_create_404(self):
        url = reverse('child', args=['test_inv', 'child_gr', 'some_gr'])
        response = self.client.put(url, **{'HTTP_X_AUTH_TOKEN': TOKEN})
        self.assertEquals(response.status_code, 404)
        self.assertJSONEqual(response.content.decode(), '{"detail":"Not found."}')

    def test_create_error(self):
        url = reverse('child', args=['test_inv', 'child_gr', 'child_gr'])
        response = self.client.put(url, **{'HTTP_X_AUTH_TOKEN': TOKEN})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content.decode(), '"group can\'t be a child of itself"')

    def test_delete(self):
        url = reverse('child', args=['test_inv', 'test_gr', 'child_gr'])
        response = self.client.delete(url, **{'HTTP_X_AUTH_TOKEN': TOKEN})
        self.assertEquals(response.status_code, 200)
        self.assertJSONEqual(response.content.decode(), '{"status":"DELETE","details":"child"}')
        self.assertFalse(Child.objects.filter(group=Group.objects.get(group="test_gr"),
                                              child=Group.objects.get(group="child_gr")).exists())


class VariableTest(TestCase):
    fixtures = ["tests/api/test_inventory.json"]

    def test_crud(self):
        # put
        url = reverse('vars_details', args=['test_inv', 'child_gr', 'test_var'])
        response = self.client.put(url, **{'HTTP_X_AUTH_TOKEN': TOKEN})
        self.assertEquals(response.status_code, 200)
        self.assertJSONEqual(response.content.decode(), '{"status":"ADD","details":"var"}')

        # put - error data
        url = reverse('vars_details', args=['test_inv', 'test_gr', 'test_var'])
        response = self.client.put(url, **{'HTTP_X_AUTH_TOKEN': TOKEN})
        self.assertEquals(response.status_code, 200)
        self.assertEqual(response.content.decode(), '"already exists"')

        # get list
        url = reverse('vars_list', args=['test_inv', 'test_gr'])
        response = self.client.get(url, **{'HTTP_X_AUTH_TOKEN': TOKEN})
        self.assertEquals(response.status_code, 200)
        self.assertEqual(response.content.decode(), '["test_var"]')

        # post
        url = reverse('vars_details', args=['test_inv', 'test_gr', 'test_var'])
        response = self.client.post(url, data="changed_val", content_type="application/json",
                                    **{'HTTP_X_AUTH_TOKEN': TOKEN})
        self.assertJSONEqual(response.content.decode(), '{"status":"UPDATE","details":"var"}')

        # get value
        url = reverse('vars_details', args=['test_inv', 'test_gr', 'test_var'])
        response = self.client.get(url, **{'HTTP_X_AUTH_TOKEN': TOKEN})
        self.assertEquals(response.status_code, 200)
        self.assertEqual(response.content.decode(), '"changed_val"')

        # delete
        url = reverse('vars_details', args=['test_inv', 'test_gr', 'test_var'])
        response = self.client.delete(url, data='test_val', **{'HTTP_X_AUTH_TOKEN': TOKEN})
        self.assertEquals(response.status_code, 200)
        self.assertEqual(response.content.decode(), '{"status":"DELETE","details":"var"}')


class HostVariableTest(TestCase):
    fixtures = ["tests/api/test_inventory.json"]

    def test_crud(self):
        # put
        url = reverse('hostvars_details', args=['test_inv', 'test.test', 'test_hostvar'])
        response = self.client.put(url, data='test_val', **{'HTTP_X_AUTH_TOKEN': TOKEN})
        self.assertEquals(response.status_code, 200)
        self.assertJSONEqual(response.content.decode(), '{"status":"ADD","details":"hostvar"}')

        # put - error data
        url = reverse('hostvars_details', args=['test_inv', 'test.test', 'test_hostvar'])
        response = self.client.put(url, data='test_val', **{'HTTP_X_AUTH_TOKEN': TOKEN})
        self.assertEquals(response.status_code, 200)
        self.assertEqual(response.content.decode(), '"already exists"')

        # post
        url = reverse('hostvars_details', args=['test_inv', 'test.test', 'test_hostvar'])
        response = self.client.post(url, data="changed_val", content_type="application/json",
                                    **{'HTTP_X_AUTH_TOKEN': TOKEN})
        self.assertJSONEqual(response.content.decode(), '{"status":"UPDATE","details":"hostvar"}')

        # get list
        url = reverse('hostvars_list', args=['test_inv', 'test.test'])
        response = self.client.get(url, **{'HTTP_X_AUTH_TOKEN': TOKEN})
        self.assertEquals(response.status_code, 200)
        self.assertEqual(response.content.decode(), '["test_hostvar"]')

        # get value
        url = reverse('hostvars_details', args=['test_inv', 'test.test', 'test_hostvar'])
        response = self.client.get(url, **{'HTTP_X_AUTH_TOKEN': TOKEN})
        self.assertEquals(response.status_code, 200)
        self.assertEqual(response.content.decode(), '"changed_val"')

        # delete
        url = reverse('hostvars_details', args=['test_inv', 'test.test', 'test_hostvar'])
        response = self.client.delete(url, data='test_val', **{'HTTP_X_AUTH_TOKEN': TOKEN})
        self.assertEquals(response.status_code, 200)
        self.assertEqual(response.content.decode(), '{"status":"DELETE","details":"hostvar"}')
