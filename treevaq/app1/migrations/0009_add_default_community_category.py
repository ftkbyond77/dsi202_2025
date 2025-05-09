# app1/migrations/0009_fix_community_category.py
from django.db import migrations

def create_default_category(apps, schema_editor):
    CommunityCategory = apps.get_model('app1', 'CommunityCategory')
    # สร้าง category เริ่มต้นถ้ายังไม่มี
    CommunityCategory.objects.get_or_create(
        id=1,
        defaults={
            'name': 'ทั่วไป',
            'slug': 'general',
            'description': 'หมวดหมู่ทั่วไป'
        }
    )

class Migration(migrations.Migration):
    dependencies = [
        ('app1', '0008_communitycategory_remove_communitypost_downvotes_and_more'),
    ]

    operations = [
        migrations.RunPython(create_default_category),
    ]