from django.contrib import admin
from .models import (
    RouteSheetAU12, AU12CrewRow, AU12SectionII, AU12WorkRow, AU12SectionIV, AU12SectionV, AU12SectionVI
)

class CrewInline(admin.TabularInline):
    model = AU12CrewRow
    extra = 0

class WorkInline(admin.TabularInline):
    model = AU12WorkRow
    extra = 0

@admin.register(RouteSheetAU12)
class RouteSheetAU12Admin(admin.ModelAdmin):
    list_display = ("number", "date", "ssps_unit", "status", "created_by", "created_at")
    list_filter = ("status", "date")
    search_fields = ("number", "ssps_unit__type_name", "ssps_unit__number")
    inlines = [CrewInline, WorkInline]

admin.site.register(AU12SectionII)
admin.site.register(AU12SectionIV)
admin.site.register(AU12SectionV)
admin.site.register(AU12SectionVI)
