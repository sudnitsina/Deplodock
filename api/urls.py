from django.conf.urls import url

from . import views

handler404 = 'api.views.not_found'
urlpatterns = [
    url(r'^inventories/?$',
        views.InventoryListView.as_view(), name='inventory_list'),
    url(r'^inventory/([A-Za-z0-9_.:-]+)/?$',
        views.InventoryDetailView.as_view(), name='inventory_details'),
    url(r'^machines/?$',
        views.MachineListView.as_view(), name='machine'),
    url(r'^machines/([A-Za-z0-9-_.:]+)/?$',
        views.MachineView.as_view(),  name='machine'),
    url(r'^inventory/([A-Za-z0-9-_.:]+)/groups/?$',
        views.GroupListView().as_view(), name='group_list'),
    url(r'^inventory/([A-Za-z0-9-_.:]+)/groups/([A-Za-z0-9-_:]+)/?$',
        views.GroupView.as_view(), name='group_details'),
    url(r'^inventory/([A-Za-z0-9-_.:]+)/groups/([A-Za-z0-9-_.:]+)/hosts/?$',
        views.HostListView.as_view(), name='host'),
    url(r'^inventory/([A-Za-z0-9-_.:]+)/groups/([A-Za-z0-9-_.:]+)/hosts/([A-Za-z0-9-_.:]+)/?$',
        views.HostView.as_view(), name='host'),
    url(r'^inventory/([A-Za-z0-9-_.:]+)/groups/([A-Za-z0-9-_.:]+)/children/?$',
        views.ChildListView.as_view(), name='child'),
    url(r'^inventory/([A-Za-z0-9-_.:]+)/groups/([A-Za-z0-9-_.:]+)/children/([A-Za-z0-9-_.:]+)/?$',
        views.ChildView.as_view(), name='child'),
    url(r'^inventory/([A-Za-z0-9-_.:]+)/groups/([A-Za-z0-9-_.:]+)/vars/?$',
        views.VariableListView.as_view(), name='vars_list'),
    url(r'^inventory/([A-Za-z0-9-_.:]+)/groups/([A-Za-z0-9-_.:]+)/vars/([A-Za-z0-9-_.:]+)/?$',
        views.VariableView.as_view(), name='vars_details'),
    url(r'^inventory/([A-Za-z0-9-_.:]+)/host/([A-Za-z0-9-_.:]+)/host_vars/?$',
        views.HostVariableListView.as_view(), name='hostvars_list'),
    url(r'^inventory/([A-Za-z0-9-_.:]+)/host/([A-Za-z0-9-_.:]+)/host_vars/([A-Za-z0-9-_.:]+)/?$',
        views.HostVariableView.as_view(), name='hostvars_details'),
]
