import base64

from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.defaults import page_not_found
from rest_framework import views
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound, ParseError
from rest_framework.response import Response

from .models import Inventory, Group, Variable, Machine, HostVariable, Host, Child
from .serializers import (
    InventorySerializer, GroupSerializer, MachineSerializer, HostSerializer, ChildSerializer,
    VariableSerializer, HostVariableSerializer, InventoryNestedSerializer)


@api_view(['GET', 'POST', 'PUT'])
def api_not_found(request, format=None):
    if request.method in ('GET', 'DELETE'):
        raise NotFound()
    if request.method in ('PUT', 'POST'):
        raise ParseError('bad request')


def not_found(request, **param):
    if request.path.split("/")[1] == 'api':
        return api_not_found(request)
    else:
        return page_not_found(request, Http404(), template_name='404.html')


class InventoryListView(views.APIView):
    def get(self, request):
        queryset = Inventory.objects.filter(user=request.user)
        serializer = InventorySerializer(queryset, many=True)
        return JsonResponse(serializer.data, safe=False)


class InventoryDetailView(views.APIView):
    def initial(self, request, inventory=None, *args, **kwargs):
        request.inventory = inventory
        super().initial(request)

    def get_object(self, user, inventory):
        return get_object_or_404(Inventory, user=user, inventory=inventory)

    def get(self, request, inventory, format=None):
        queryset = self.get_object(request.user, inventory)
        serializer = InventoryNestedSerializer()
        res = serializer.data(queryset)
        return Response(res)

    def put(self, request, inventory):
        inv = {'inventory': inventory, 'user': request.user.pk}
        serializer = InventorySerializer(data=inv)
        if not serializer.is_valid():
            return Response([val[0] for key, val in serializer.errors.items()][0])
        if request.body:
            data = request.body.decode("utf-8")
            try:
                serializer.upload(data)
            except ValueError as e:
                return HttpResponse(e)
            except Exception as e:
                return HttpResponse('invalid data')
            return HttpResponse('done')
        else:
            serializer.save()
            return Response({"status": "ADD", "details": "inventory"})

    def delete(self, request, inventory):
        inventory = get_object_or_404(Inventory, user=request.user, inventory=inventory)
        inventory.delete()
        return Response({"status": "DELETE", "details": "inventory"})


class GroupListView(views.APIView):
    def initial(self, request, inventory=None, *args, **kwargs):
        request.inventory = inventory
        super().initial(request)

    def get(self, request, inventory, group=None):
        i = get_object_or_404(Inventory, user=request.user, inventory=inventory)
        queryset = Group.objects.filter(inventory=i)
        serializer = GroupSerializer(queryset, many=True)
        return JsonResponse(serializer.data, safe=False)


class GroupView(views.APIView):
    def initial(self, request, inventory=None, *args, **kwargs):
        request.inventory = inventory
        super().initial(request)

    def put(self, request, inventory, group):
        inv = Inventory.objects.get(user=request.user, inventory=inventory).pk
        data = {'inventory': inv, 'group': group}
        serializer = GroupSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "ADD", "details": "group"})
        return Response([val[0] for key, val in serializer.errors.items()][0])

    def delete(self, request, inventory, group):
        inventory = get_object_or_404(Inventory, user=request.user, inventory=inventory)
        group = get_object_or_404(Group, inventory=inventory, group=group)
        group.delete()
        return Response({"status": "DELETE", "details": "group"})


class MachineListView(views.APIView):
    def get(self, request):
        queryset = Machine.objects.filter(user=request.user)
        serializer = MachineSerializer(queryset, many=True)
        data = {"machines": serializer.data}
        if request.GET.get('json'):
            return render(request, "dashboard/table.html", data)
        return Response(serializer.data)


class MachineView(views.APIView):
    def initial(self, request, *args, **kwargs):
        super().initial(request)

    def put(self, request, machine):
        data = {'machine': machine, 'user': request.user.pk}
        serializer = MachineSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "ADD", "details": "machine"})
        return Response([val[0] for key, val in serializer.errors.items()][0])

    def delete(self, request, machine):
        machine = get_object_or_404(Machine, machine=machine, user=request.user)
        machine.delete()
        return Response({"status": "DELETE", "details": "machine"})


class HostListView(views.APIView):
    def get(self, request, inventory, group):
        inventory = get_object_or_404(Inventory, inventory=inventory,
                                      user=request.user)
        group = get_object_or_404(Group, inventory=inventory, group=group)
        queryset = Host.objects.filter(group=group)
        serializer = HostSerializer(queryset, many=True)
        return Response(serializer.data)


class HostView(views.APIView):
    def initial(self, request, inventory, group, host, *args, **kwargs):
        self.inventory = get_object_or_404(Inventory, inventory=inventory, user=request.user)
        self.group = get_object_or_404(Group, inventory=self.inventory, group=group)
        self.machine = get_object_or_404(Machine, machine=host)
        super().initial(request)

    def put(self, request, inventory, group, host):
        data = {'group': self.group.pk, 'host': self.machine.pk}
        serializer = HostSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "ADD", "details": "host"})
        return Response([val[0] for key, val in serializer.errors.items()][0])

    def delete(self, request, inventory, group, host):
        get_object_or_404(Host, host=self.machine, group=self.group).delete()
        return Response({"status": "DELETE", "details": "host"})


class ChildListView(views.APIView):
    def get(self, request, inventory, group):
        inventory = Inventory.objects.get(inventory=inventory, user=request.user)
        group = get_object_or_404(Group, inventory=inventory, group=group)
        queryset = Child.objects.filter(group=group)
        serializer = ChildSerializer(queryset, many=True)
        return Response(serializer.data)


class ChildView(views.APIView):
    def put(self, request, inventory, group, child):
        inventory = get_object_or_404(Inventory, inventory=inventory, user=request.user)
        group = get_object_or_404(Group, inventory=inventory, group=group)
        child = get_object_or_404(Group, inventory=inventory, group=child)
        data = {'group': group.pk, 'child': child.pk}
        serializer = ChildSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "ADD", "details": "child"})
        return Response([val[0] for key, val in serializer.errors.items()][0])

    def delete(self, request, inventory, group, child):
        inventory = get_object_or_404(Inventory, inventory=inventory, user=request.user)
        group = get_object_or_404(Group, inventory=inventory, group=group)
        get_object_or_404(Child, group=group, child__group=child).delete()
        return Response({"status": "DELETE", "details": "child"})


class VariableListView(views.APIView):
    def get(self, request, inventory, group):
        inventory = get_object_or_404(Inventory, inventory=inventory, user=request.user)
        group = get_object_or_404(Group, inventory=inventory, group=group)

        # handle request from dashboard
        if request.auth is None:
            var = Variable.objects.filter(group=group).values('variable', 'value')
            data = {
                v["variable"]: base64.b64decode(v["value"]).decode() for v in var}
            return Response(data)

        # handle request from api
        queryset = Variable.objects.filter(group=group)
        serializer = VariableSerializer(queryset, many=True)
        return Response(serializer.data)


class VariableView(views.APIView):
    def get(self, request, inventory, group, variable):
        inventory = get_object_or_404(Inventory, inventory=inventory, user=request.user)
        group = get_object_or_404(Group, inventory=inventory, group=group)
        var = get_object_or_404(Variable, group=group, variable=variable)
        return Response(base64.b64decode(var.value).decode())

    def put(self, request, inventory, group, variable):
        inventory = get_object_or_404(Inventory, inventory=inventory, user=request.user)
        group = get_object_or_404(Group, inventory=inventory, group=group)
        value = base64.b64encode(request.body).decode()
        data = {'group': group.pk, 'variable': variable, 'value': value}
        serializer = VariableSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "ADD", "details": "var"})
        return Response([val[0] for key, val in serializer.errors.items()][0])

    def post(self, request, inventory, group, variable):
        inventory = get_object_or_404(Inventory, inventory=inventory, user=request.user)
        group = get_object_or_404(Group, inventory=inventory, group=group)
        value = base64.b64encode(request.body).decode()
        var = get_object_or_404(Variable, group=group, variable=variable)
        var.value = value
        var.save()

        return Response({"status": "UPDATE", "details": "var"})

    def delete(self, request, inventory, group, variable):
        inventory = get_object_or_404(Inventory, inventory=inventory, user=request.user)
        group = get_object_or_404(Group, inventory=inventory, group=group)
        get_object_or_404(Variable, group=group, variable=variable).delete()
        return Response({"status": "DELETE", "details": "var"})


class HostVariableListView(views.APIView):
    def get(self, request, inventory, host):
        inventory = get_object_or_404(Inventory, inventory=inventory, user=request.user)
        host = get_object_or_404(Machine, machine=host, user=request.user)

        # handle request from dashboard
        if request.auth is None:
            var = HostVariable.objects.filter(inventory=inventory,
                                              host=host).values('variable', 'value')
            data = {v["variable"]: base64.b64decode(v["value"]).decode() for v in var}
            return Response(data)

        # handle request from api
        queryset = HostVariable.objects.filter(inventory=inventory, host=host)
        serializer = VariableSerializer(queryset, many=True)
        return Response(serializer.data)


class HostVariableView(views.APIView):
    def get(self, request, inventory, host, variable):
        inventory = get_object_or_404(Inventory, inventory=inventory, user=request.user)
        host = get_object_or_404(Machine, machine=host, user=request.user)
        var = get_object_or_404(HostVariable, inventory=inventory, host=host, variable=variable)
        return Response(base64.b64decode(var.value).decode())

    def put(self, request, inventory, host, variable):
        inventory = get_object_or_404(Inventory, inventory=inventory, user=request.user)
        host = get_object_or_404(Machine, machine=host, user=request.user)
        value = base64.b64encode(request.body).decode()
        data = {'inventory': inventory.pk,
                'host': host.pk,
                'variable': variable,
                'value': value}
        serializer = HostVariableSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "ADD", "details": "hostvar"})
        return Response([val[0] for key, val in serializer.errors.items()][0])

    def post(self, request, inventory, host, variable):
        inventory = get_object_or_404(Inventory, inventory=inventory, user=request.user)
        host = get_object_or_404(Machine, machine=host, user=request.user)
        value = base64.b64encode(request.body).decode()
        var = get_object_or_404(HostVariable, inventory=inventory, host=host, variable=variable)
        var.value = value
        var.save()
        return Response({"status": "UPDATE", "details": "hostvar"})

    def delete(self, request, inventory, host, variable):
        inventory = get_object_or_404(Inventory, inventory=inventory, user=request.user)
        host = get_object_or_404(Machine, machine=host, user=request.user)
        get_object_or_404(
            HostVariable, inventory=inventory, host=host, variable=variable
        ).delete()
        return Response({"status": "DELETE", "details": "hostvar"})