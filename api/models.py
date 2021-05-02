from django.db import models
from datetime import datetime


class Vehicle(models.Model):
    vehicle_type = models.CharField(max_length=10, primary_key=True)
    vehicle_capacity = models.IntegerField()

    def __str__(self):
        return self.vehicle_type

class DeliveryPartner(models.Model):
    delivery_partner_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    vehicle_type = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    date = models.DateTimeField(default=datetime.now())
    order_id = models.IntegerField(primary_key=True, unique=True)
    order_weight = models.IntegerField()

    def __str__(self):
        return str(self.order_id)


class AssignedOrder(models.Model):
    order_assigned_date = models.DateTimeField(default=datetime.now())
    id = models.AutoField(primary_key=True)
    vehicle_type = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE)
    delivery_partner_id = models.ForeignKey(
        DeliveryPartner, on_delete=models.CASCADE)
    list_order_ids_assigned = models.ManyToManyField(Order)
    total_weight_of_order = models.IntegerField(default=0)



    # def __str__(self):
    #     return str(self.delivery_partner_id)
