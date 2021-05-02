# Generated by Django 3.2 on 2021-05-01 19:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('date', models.DateTimeField()),
                ('order_id', models.IntegerField(primary_key=True, serialize=False, unique=True)),
                ('order_weight', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Vehicle',
            fields=[
                ('vehicle_type', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('vehicle_capacity', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='DeliveryPartner',
            fields=[
                ('delivery_partner_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('is_available', models.BooleanField(default=True)),
                ('vehicle_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.vehicle')),
            ],
        ),
        migrations.CreateModel(
            name='AssignedOrder',
            fields=[
                ('order_assigned_date', models.DateTimeField()),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('delivery_partner_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.deliverypartner')),
                ('list_order_ids_assigned', models.ManyToManyField(to='api.Order')),
                ('vehicle_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.vehicle')),
            ],
        ),
    ]
