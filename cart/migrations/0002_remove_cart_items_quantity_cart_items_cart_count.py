# Generated by Django 5.1.3 on 2024-11-30 16:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart_items',
            name='quantity',
        ),
        migrations.AddField(
            model_name='cart_items',
            name='cart_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]