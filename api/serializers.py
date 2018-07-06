import base64
import json
from collections import defaultdict

from django.db import transaction
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .ini_serializer import serializer as ini_serializer
from .models import Inventory, Group, Variable, Machine, HostVariable, Host, Child


class InventorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Inventory
        fields = ('inventory', 'user')
        validators = [
            UniqueTogetherValidator(
                queryset=Inventory.objects.all(),
                fields=('inventory', 'user'),
                message='already exists'
            )]

    def to_representation(self, obj):
        return str(obj)

    @transaction.atomic
    def upload(self, data):

        inventory = self.save()
        try:
            data = json.loads(data)
        except ValueError:
            data = ini_serializer(data)
        user = inventory.user
        ch_list = []
        var_list = []
        host_list = []
        host_vars_list = []

        # creating groups
        for gr in data.keys():
            if gr != '_meta':
                if Group.objects.filter(inventory=inventory, group=gr).exists():
                    g = Group.objects.get(inventory=inventory, group=gr)
                else:
                    g = Group(inventory=inventory, group=gr)
                    g.clean_fields(exclude=['id', 'inventory'])
                    g.save()

                # preparing vars/hosts/children
                if data[gr].get("vars") and isinstance(data[gr].get("vars"), dict):
                    for i in data[gr].get("vars"):
                        var = Variable(
                            group=g, variable=i,
                            value=base64.b64encode(bytes(str(data[gr]["vars"][i]), encoding='utf-8')).decode())
                        var.clean_fields(exclude=['id', 'group'])
                        var_list.append(var)

                if data[gr].get("hosts"):
                    if not isinstance(data[gr].get("hosts"), list):
                        raise ValueError('hosts should be list')
                    for i in set(data[gr].get("hosts")):
                        if Machine(machine=i, user=user).clean_fields() is None:
                            h = Host(host=Machine.objects.get_or_create(machine=i, user=user)[0], group=g)
                            host_list.append(h)

                if data[gr].get("children"):
                    if not isinstance(data[gr].get("children"), list):
                        raise ValueError('children should be list')
                    for i in set(data[gr].get("children")):
                        if Group(inventory=inventory, group=i).clean_fields() is None:
                            ch = Child(child=Group.objects.get_or_create(inventory=inventory, group=i)[0], group=g)
                            ch_list.append(ch)
            else:
                for host in data["_meta"]["hostvars"]:
                    for var in data["_meta"]["hostvars"].get(host):
                        if Machine(machine=host, user=user).clean_fields() is None:
                            machine = Machine.objects.get_or_create(machine=host, user=user)[0]
                        else:
                            raise ValueError()
                        hostvar = HostVariable(
                            inventory=inventory,
                            host=machine,
                            variable=var,
                            value=base64.b64encode(bytes(str(data["_meta"]["hostvars"][host][var]),
                                                         encoding='utf-8')).decode())
                        host_vars_list.append(hostvar)

        # creating vars/hosts/children
        HostVariable.objects.bulk_create(host_vars_list)
        Child.objects.bulk_create(ch_list)
        Host.objects.bulk_create(host_list)
        Variable.objects.bulk_create(var_list)


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('group', 'inventory')
        validators = [
            UniqueTogetherValidator(
                queryset=Group.objects.all(),
                fields=('group', 'inventory'),
                message='already exists'
            )]

    def to_representation(self, obj):
        return str(obj)


class MachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = ('machine', 'user')
        validators = [
            UniqueTogetherValidator(
                queryset=Machine.objects.all(),
                fields=('machine', 'user'),
                message='already exists'
            )]

    def to_representation(self, obj):
        return obj.machine


class HostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Host
        fields = ('group', 'host')
        validators = [
            UniqueTogetherValidator(
                queryset=Host.objects.all(),
                fields=('group', 'host'),
                message='already exists'
            )]

    def to_representation(self, obj):
        return obj.host.machine


class ChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Child
        fields = ('group', 'child')
        validators = [
            UniqueTogetherValidator(
                queryset=Child.objects.all(),
                fields=('group', 'child'),
                message='already exists'
            )]

    def to_representation(self, obj):
        return obj.child.group

    def validate(self, data):
        if data["group"] == data["child"]:
            raise serializers.ValidationError("group can't be a child of itself")
        return data


class VariableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variable
        fields = ('group', 'variable', 'value')
        validators = [
            UniqueTogetherValidator(
                queryset=Variable.objects.all(),
                fields=('group', 'variable'),
                message='already exists'
            )]

    def to_representation(self, obj):
        return obj.variable


class HostVariableSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostVariable
        fields = ('inventory', 'host', 'variable', 'value')
        validators = [
            UniqueTogetherValidator(
                queryset=HostVariable.objects.all(),
                fields=('inventory', 'host', 'variable'),
                message='already exists'
            )]

    def to_representation(self, obj):
        return obj.variable


class InventoryNestedSerializer:
    def data(self, obj):
        ret = {str(i): {
            "vars": {var: base64.b64decode(val).decode() for var, val in
                     i.variable_set.values_list('variable', 'value')},
            "hosts": i.host_set.values_list('host__machine', flat=True),
            "children": i.parent.values_list('child__group', flat=True)
        } for i in obj.group_set.all()}
        all_ = {'all': {'vars': {'inventory_name': str(obj)}, 'hosts': [], 'children': []}}
        meta = defaultdict(dict)
        host = obj.hostvariable_set.values("host__machine", 'value', 'variable')
        for i in host:
            meta[i["host__machine"]][i["variable"]] = base64.b64decode(i["value"]).decode()
        if meta != {}:
            ret["_meta"] = dict([("hostvars", meta)])
        ret.update(all_)
        return ret
