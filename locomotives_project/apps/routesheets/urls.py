from django.urls import path
from . import views

app_name = "routesheets"

urlpatterns = [
    path("au12/", views.AU12ListView.as_view(), name="au12_list"),
    path("au12/create/", views.AU12CreateView.as_view(), name="au12_create"),
    path("au12/<int:pk>/", views.AU12DetailView.as_view(), name="au12_detail"),

    path("au12/<int:pk>/med-pre/", views.au12_med_pre, name="au12_med_pre"),
    path("au12/<int:pk>/issue/", views.au12_issue_by_master, name="au12_issue"),

    path("au12/<int:pk>/section/i/", views.au12_section_i, name="au12_sec_i"),
    path("au12/<int:pk>/section/ii/", views.au12_section_ii, name="au12_sec_ii"),
    path("au12/<int:pk>/section/iii/", views.au12_section_iii, name="au12_sec_iii"),
    path("au12/<int:pk>/section/iv/", views.au12_section_iv, name="au12_sec_iv"),
    path("au12/<int:pk>/section/v/", views.au12_section_v, name="au12_sec_v"),
    path("au12/<int:pk>/section/vi/", views.au12_section_vi, name="au12_sec_vi"),

    path("au12/<int:pk>/med-post/", views.au12_med_post, name="au12_med_post"),
    path("au12/<int:pk>/finalize/", views.au12_finalize, name="au12_finalize"),

    path("au12/<int:pk>/export/pdf/", views.au12_export_pdf, name="au12_export_pdf"),
    path("au12/<int:pk>/export/excel/", views.au12_export_excel, name="au12_export_excel"),

    path("analytics/fuel/", views.analytics_fuel, name="analytics_fuel"),
]
