# Generated by Django 5.1.6 on 2025-03-03 19:43

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ChildInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('student_id', models.CharField(max_length=50)),
                ('age', models.IntegerField()),
                ('allergies', models.TextField()),
                ('other_allergies', models.TextField(blank=True)),
            ],
        ),
    ]
