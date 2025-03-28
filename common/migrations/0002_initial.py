# Generated by Django 5.0.3 on 2025-03-23 11:29

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('common', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to=settings.AUTH_USER_MODEL, verbose_name='작성자'),
        ),
        migrations.AddIndex(
            model_name='review',
            index=models.Index(fields=['content_type', 'object_id'], name='common_revi_content_5b84b1_idx'),
        ),
    ]
