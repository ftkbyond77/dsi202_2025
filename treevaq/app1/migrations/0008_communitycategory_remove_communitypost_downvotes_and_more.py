# app1/migrations/0008_communitycategory_remove_communitypost_downvotes_and_more.py
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

def create_default_category(apps, schema_editor):
    CommunityCategory = apps.get_model('app1', 'CommunityCategory')
    # สร้าง category เริ่มต้นถ้ายังไม่มี
    CommunityCategory.objects.get_or_create(
        id=1,
        defaults={
            'name': 'ทั่วไป',
            'slug': 'general',
            'description': 'หมวดหมู่ทั่วไปสำหรับโพสต์ทั้งหมด',
            'created_at': '2025-05-10T00:00:00Z'  # ใช้เวลาปัจจุบันหรือตามที่ต้องการ
        }
    )

class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app1', '0007_order'),
    ]

    operations = [
        # 1. สร้างตาราง CommunityCategory ก่อน
        migrations.CreateModel(
            name='CommunityCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'Community Categories',
            },
        ),

        # 2. สร้าง default category ทันทีหลังจากสร้างตาราง
        migrations.RunPython(create_default_category),

        # 3. เอาฟิลด์เดิมออก
        migrations.RemoveField(
            model_name='communitypost',
            name='downvotes',
        ),
        migrations.RemoveField(
            model_name='communitypost',
            name='parent',
        ),
        migrations.RemoveField(
            model_name='communitypost',
            name='post_type',
        ),
        migrations.RemoveField(
            model_name='communitypost',
            name='product',
        ),
        migrations.RemoveField(
            model_name='communitypost',
            name='rating',
        ),
        migrations.RemoveField(
            model_name='communitypost',
            name='upvotes',
        ),

        # 4. เพิ่มฟิลด์ใหม่
        migrations.AddField(
            model_name='communitypost',
            name='slug',
            field=models.SlugField(blank=True, unique=True),
        ),
        migrations.AddField(
            model_name='communitypost',
            name='title',
            field=models.CharField(default='Default Title', max_length=200),
            preserve_default=False,
        ),

        # 5. สร้างโมเดลใหม่ๆ
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(choices=[(1, '1 - Poor'), (2, '2 - Fair'), (3, '3 - Good'), (4, '4 - Very Good'), (5, '5 - Excellent')])),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='app1.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='app1.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='app1.communitypost')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='app1.question')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to=settings.AUTH_USER_MODEL)),
            ],
        ),

        # 6. เพิ่ม foreign key category หลังจากที่สร้าง default category แล้ว
        migrations.AddField(
            model_name='communitypost',
            name='category',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='app1.communitycategory'),
            preserve_default=False,
        ),

        # 7. สร้างโมเดล PostLike
        migrations.CreateModel(
            name='PostLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='likes', to='app1.communitypost')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_likes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'post')},
            },
        ),
    ]