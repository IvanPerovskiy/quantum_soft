# Generated by Django 3.2.10 on 2022-06-07 15:35

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cache',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tree_id', models.BigIntegerField(db_index=True)),
                ('parent_id', models.BigIntegerField(blank=True, db_index=True, null=True)),
                ('value', models.CharField(max_length=200)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_sent', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Tree',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=200)),
                ('depth', models.BigIntegerField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('updated', models.DateTimeField(default=datetime.datetime.now)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.tree')),
            ],
        ),
    ]
