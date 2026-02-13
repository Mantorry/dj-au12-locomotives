from django.contrib import admin
from .models import Enterprise, Station, FuelType, LubricantType, SSPSUnit

admin.site.register(Enterprise)
admin.site.register(Station)
admin.site.register(FuelType)
admin.site.register(LubricantType)
admin.site.register(SSPSUnit)
