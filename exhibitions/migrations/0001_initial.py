# Generated by Django 5.0.3 on 2025-06-16 07:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Exhibition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='생성일')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='수정일')),
                ('title', models.CharField(max_length=200, verbose_name='제목')),
                ('description', models.TextField(blank=True, verbose_name='설명')),
                ('venue', models.CharField(max_length=100, verbose_name='장소')),
                ('start_date', models.DateField(verbose_name='시작일')),
                ('end_date', models.DateField(verbose_name='종료일')),
                ('status', models.CharField(choices=[('upcoming', '예정'), ('ongoing', '진행중'), ('ended', '종료')], default='upcoming', max_length=10, verbose_name='상태')),
                ('image', models.ImageField(blank=True, null=True, upload_to='exhibitions/images/', verbose_name='전시 이미지')),
                ('map_url', models.URLField(blank=True, verbose_name='네이버 지도 링크')),
                ('museum_url', models.URLField(blank=True, verbose_name='미술관 링크')),
                ('likes_count', models.PositiveIntegerField(default=0, verbose_name='좋아요 수')),
            ],
            options={
                'verbose_name': '전시',
                'verbose_name_plural': '전시 목록',
                'db_table': 'exhibition',
                'ordering': ['-start_date'],
                'indexes': [models.Index(fields=['-start_date'], name='exhibition_start_d_cc6a63_idx'), models.Index(fields=['status', '-start_date'], name='exhibition_status_742a9b_idx'), models.Index(fields=['-likes_count'], name='exhibition_likes_c_0ea087_idx'), models.Index(fields=['venue'], name='exhibition_venue_00641c_idx'), models.Index(fields=['start_date', 'end_date'], name='exhibition_start_d_4dc2ac_idx'), models.Index(fields=['-created_at'], name='exhibition_created_941e9e_idx'), models.Index(fields=['id'], name='exhibition_id_971e1f_idx')],
            },
        ),
        migrations.CreateModel(
            name='ExhibitionLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='생성일')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='수정일')),
                ('exhibition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='exhibitions.exhibition', verbose_name='전시')),
            ],
            options={
                'verbose_name': '전시 좋아요',
                'verbose_name_plural': '전시 좋아요 목록',
                'db_table': 'exhibition_like',
            },
        ),
    ]
