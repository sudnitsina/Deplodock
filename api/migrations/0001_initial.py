# Generated by Django 2.0 on 2018-07-05 16:22

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Child',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'ordering': ['child'],
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.CharField(max_length=256, validators=[django.core.validators.RegexValidator('^[A-Za-z0-9-_.:]+$')])),
            ],
            options={
                'ordering': ['group'],
            },
        ),
        migrations.CreateModel(
            name='Host',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Group')),
            ],
            options={
                'ordering': ['host'],
            },
        ),
        migrations.CreateModel(
            name='HostVariable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('variable', models.CharField(max_length=256, validators=[django.core.validators.RegexValidator('^[A-Za-z0-9-_.:]+$')])),
                ('value', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['variable'],
            },
        ),
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inventory', models.CharField(max_length=256, validators=[django.core.validators.RegexValidator('^[A-Za-z0-9-_.:]+$')])),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['inventory'],
            },
        ),
        migrations.CreateModel(
            name='Machine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('machine', models.CharField(max_length=256, validators=[django.core.validators.RegexValidator('^[A-Za-z0-9-_.:]+$')])),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['machine'],
            },
        ),
        migrations.CreateModel(
            name='Variable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('variable', models.CharField(max_length=256, validators=[django.core.validators.RegexValidator('^[A-Za-z0-9-_.:]+$')])),
                ('value', models.TextField(blank=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Group')),
            ],
            options={
                'ordering': ['variable'],
            },
        ),
        migrations.AddField(
            model_name='hostvariable',
            name='host',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Machine'),
        ),
        migrations.AddField(
            model_name='hostvariable',
            name='inventory',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Inventory'),
        ),
        migrations.AddField(
            model_name='host',
            name='host',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Machine'),
        ),
        migrations.AddField(
            model_name='group',
            name='inventory',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Inventory'),
        ),
        migrations.AddField(
            model_name='child',
            name='child',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='child', to='api.Group'),
        ),
        migrations.AddField(
            model_name='child',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parent', to='api.Group'),
        ),
        migrations.AlterUniqueTogether(
            name='variable',
            unique_together={('group', 'variable')},
        ),
        migrations.AlterUniqueTogether(
            name='machine',
            unique_together={('machine', 'user')},
        ),
        migrations.AlterUniqueTogether(
            name='inventory',
            unique_together={('inventory', 'user')},
        ),
        migrations.AlterUniqueTogether(
            name='hostvariable',
            unique_together={('inventory', 'host', 'variable')},
        ),
        migrations.AlterUniqueTogether(
            name='host',
            unique_together={('group', 'host')},
        ),
        migrations.AlterUniqueTogether(
            name='group',
            unique_together={('group', 'inventory')},
        ),
        migrations.AlterUniqueTogether(
            name='child',
            unique_together={('group', 'child')},
        ),
    ]
