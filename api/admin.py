from django.contrib import admin
from api.models import Vehicle,DeliveryPartner,Order,AssignedOrder

# Register your models here.
admin.site.register(Vehicle)
admin.site.register(DeliveryPartner)
admin.site.register(Order)
admin.site.register(AssignedOrder)

