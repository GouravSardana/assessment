# Generated by Django 3.2 on 2021-05-02 17:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_alter_assignedorder_order_assigned_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignedorder',
            name='order_assigned_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
