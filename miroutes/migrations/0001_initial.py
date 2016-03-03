# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-27 11:36
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import djgeojson.fields
import miroutes.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('area_name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country_name', models.CharField(max_length=100)),
                ('country_code', models.CharField(max_length=4)),
            ],
        ),
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('route_name', models.CharField(max_length=100)),
                ('route_grade', models.CharField(choices=[(b'5', b'5b'), (b'5b', b'5b'), (b'5c', b'5c'), (b'6a', b'6a'), (b'6b', b'6b')], default=b'5b', max_length=2)),
                ('geom', djgeojson.fields.LineStringField(default=dict)),
            ],
        ),
        migrations.CreateModel(
            name='Spot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('spot_name', models.CharField(max_length=100)),
                ('geom', djgeojson.fields.PointField(default=dict)),
                ('spot_area', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='miroutes.Area')),
            ],
        ),
        migrations.CreateModel(
            name='Wall',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wall_name', models.CharField(max_length=100)),
                ('geom', djgeojson.fields.PointField(default=dict)),
                ('background_img', models.ImageField(blank=True, upload_to=miroutes.models.get_bg_img_upload_path)),
                ('wall_spot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='miroutes.Spot')),
            ],
        ),
        migrations.AddField(
            model_name='route',
            name='route_wall',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='miroutes.Wall'),
        ),
        migrations.AddField(
            model_name='area',
            name='area_country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='miroutes.Country'),
        ),
    ]