# Generated by Django 5.0.3 on 2025-05-06 09:40

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('artworks', '0002_initial'),
        ('docents', '0001_initial'),
        ('exhibitions', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='docent',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='docents', to=settings.AUTH_USER_MODEL, verbose_name='작성자'),
        ),
        migrations.AddField(
            model_name='docent',
            name='exhibition',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='docents', to='exhibitions.exhibition', verbose_name='전시'),
        ),
        migrations.AddField(
            model_name='docenthighlight',
            name='docent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='highlights', to='docents.docent', verbose_name='도슨트'),
        ),
        migrations.AddField(
            model_name='docenthighlight',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='docent_highlights', to=settings.AUTH_USER_MODEL, verbose_name='사용자'),
        ),
        migrations.AddField(
            model_name='docentitem',
            name='artwork',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='docent_items', to='artworks.artwork', verbose_name='작품'),
        ),
        migrations.AddField(
            model_name='docentitem',
            name='docent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='docents.docent', verbose_name='도슨트'),
        ),
        migrations.AddField(
            model_name='docenthighlight',
            name='docent_item',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='highlights', to='docents.docentitem', verbose_name='도슨트 항목'),
        ),
        migrations.AddField(
            model_name='docentlike',
            name='docent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='docents.docent'),
        ),
        migrations.AddField(
            model_name='docentlike',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='docentitem',
            unique_together={('docent', 'order')},
        ),
        migrations.AlterUniqueTogether(
            name='docentlike',
            unique_together={('docent', 'user')},
        ),
    ]
