from django.urls import path
from . import views

app_name = "panel"

urlpatterns = [
    path("", views.PanelHomeView.as_view(), name="home"),

    path("users/", views.PanelUserList.as_view(), name="user_list"),
    path("users/<int:pk>/edit/", views.PanelUserEdit.as_view(), name="user_edit"),

    path("directory/enterprises/", views.EnterpriseList.as_view(), name="enterprise_list"),
    path("directory/enterprises/create/", views.EnterpriseCreate.as_view(), name="enterprise_create"),
    path("directory/enterprises/<int:pk>/edit/", views.EnterpriseEdit.as_view(), name="enterprise_edit"),
    path("directory/enterprises/<int:pk>/delete/", views.EnterpriseDelete.as_view(), name="enterprise_delete"),

    path("directory/stations/", views.StationList.as_view(), name="station_list"),
    path("directory/stations/create/", views.StationCreate.as_view(), name="station_create"),
    path("directory/stations/<int:pk>/edit/", views.StationEdit.as_view(), name="station_edit"),
    path("directory/stations/<int:pk>/delete/", views.StationDelete.as_view(), name="station_delete"),

    path("directory/fuel/", views.FuelTypeList.as_view(), name="fuel_list"),
    path("directory/fuel/create/", views.FuelTypeCreate.as_view(), name="fuel_create"),
    path("directory/fuel/<int:pk>/edit/", views.FuelTypeEdit.as_view(), name="fuel_edit"),
    path("directory/fuel/<int:pk>/delete/", views.FuelTypeDelete.as_view(), name="fuel_delete"),

    path("directory/lube/", views.LubricantTypeList.as_view(), name="lube_list"),
    path("directory/lube/create/", views.LubricantTypeCreate.as_view(), name="lube_create"),
    path("directory/lube/<int:pk>/edit/", views.LubricantTypeEdit.as_view(), name="lube_edit"),
    path("directory/lube/<int:pk>/delete/", views.LubricantTypeDelete.as_view(), name="lube_delete"),

    path("directory/ssps/", views.SSPSUnitList.as_view(), name="ssps_list"),
    path("directory/ssps/create/", views.SSPSUnitCreate.as_view(), name="ssps_create"),
    path("directory/ssps/<int:pk>/edit/", views.SSPSUnitEdit.as_view(), name="ssps_edit"),
    path("directory/ssps/<int:pk>/delete/", views.SSPSUnitDelete.as_view(), name="ssps_delete"),

    path("directory/brigades/", views.BrigadeList.as_view(), name="brigade_list"),
    path("directory/brigades/create/", views.BrigadeCreate.as_view(), name="brigade_create"),
    path("directory/brigades/<int:pk>/edit/", views.BrigadeEdit.as_view(), name="brigade_edit"),
    path("directory/brigades/<int:pk>/delete/", views.BrigadeDelete.as_view(), name="brigade_delete"),
]