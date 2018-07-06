from django.contrib.auth.models import User
from django.test import TestCase

from api import models


class MachineTest(TestCase):
    def test_init(self):
        obj = models.Machine(machine="my_machine")
        self.assertEqual(str(obj), "my_machine")

class InventoryTest(TestCase):
    def test_init(self):
        obj = models.Inventory(inventory="my_inv")
        self.assertEqual(str(obj), "my_inv")


class GroupTest(TestCase):
    def test_init(self):
        obj = models.Group(group="my_group")
        self.assertEqual(str(obj), "my_group")


class VariableTest(TestCase):
    def test_init(self):
        obj = models.Variable(variable="my_var", value="my_val")
        self.assertEqual(str(obj), "my_var")

class HostTest(TestCase):
    def test_init(self):
        mach = models.Machine(machine="my_machine")
        obj = models.Host(host=mach)
        self.assertEqual(str(obj), "my_machine")


class ChildTest(TestCase):
    def test_init(self):
        parent = models.Group(group="p_group")
        child = models.Group(group="c_group")
        obj = models.Child(group=parent, child=child)
        self.assertEqual(str(obj), "c_group")


class HostVariableTest(TestCase):
    def test_init(self):
        obj = models.HostVariable(variable="my_var", value="my_val")
        self.assertEqual(str(obj), "my_var")


class InventorySaveTest(TestCase):
    def setUp(self):
        self.user = User(username="tester")
        self.user.save()

    def test_inventory(self):
        inv = models.Inventory(inventory="saved_inventory", user=self.user)
        inv.save()
        self.assertTrue(models.Inventory.objects.filter(inventory="saved_inventory", user=self.user).exists())

