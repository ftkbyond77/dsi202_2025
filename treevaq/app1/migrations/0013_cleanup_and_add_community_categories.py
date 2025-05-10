from django.db import migrations

def cleanup_and_add_categories(apps, schema_editor):
    CommunityCategory = apps.get_model('app1', 'CommunityCategory')
    CommunityPost = apps.get_model('app1', 'CommunityPost')

    # 1. เก็บหมวดหมู่ "ทั่วไป" (id=1) ไว้เป็นหมวดหมู่หลัก
    try:
        default_category = CommunityCategory.objects.get(id=1)
    except CommunityCategory.DoesNotExist:
        default_category = CommunityCategory.objects.create(
            id=1,
            name='ทั่วไป',
            slug='general',
            description='หมวดหมู่ทั่วไปสำหรับโพสต์ทั้งหมด'
        )

    # 2. ค้นหาและลบหมวดหมู่ที่ซ้ำซ้อน (เช่น 'General', 'ทั่วไป' ที่ไม่ใช่ id=1)
    duplicate_categories = CommunityCategory.objects.filter(name__in=['ทั่วไป', 'General']).exclude(id=1)
    for category in duplicate_categories:
        # อัปเดตโพสต์ที่เชื่อมโยงกับหมวดหมู่ที่ซ้ำซ้อนให้ชี้ไปที่ default_category
        CommunityPost.objects.filter(category=category).update(category=default_category)
        # ลบหมวดหมู่ที่ซ้ำซ้อน
        category.delete()

    # 3. สร้างหมวดหมู่ใหม่ถ้ายังไม่มี
    new_categories = [
        {'name': 'Product Reviews', 'slug': 'product-reviews', 'description': 'หมวดหมู่สำหรับรีวิวสินค้า'},
        {'name': 'Tips & Guides', 'slug': 'tips-guides', 'description': 'หมวดหมู่สำหรับเคล็ดลับและคู่มือ'},
        {'name': 'Comparisons', 'slug': 'comparisons', 'description': 'หมวดหมู่สำหรับการเปรียบเทียบสินค้า'},
        {'name': 'Project Showcases', 'slug': 'project-showcases', 'description': 'หมวดหมู่สำหรับแสดงผลงานโครงการ'},
        {'name': 'Questions', 'slug': 'questions', 'description': 'หมวดหมู่สำหรับคำถามและการสนทนา'},
    ]

    for cat in new_categories:
        CommunityCategory.objects.get_or_create(
            name=cat['name'],
            defaults={
                'slug': cat['slug'],
                'description': cat['description']
            }
        )

def reverse_cleanup_and_add_categories(apps, schema_editor):
    CommunityCategory = apps.get_model('app1', 'CommunityCategory')
    # ลบหมวดหมู่ที่สร้างใหม่เมื่อย้อนกลับ
    CommunityCategory.objects.filter(
        name__in=[
            'Product Reviews',
            'Tips & Guides',
            'Comparisons',
            'Project Showcases',
            'Questions'
        ]
    ).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('app1', '0012_alter_communitycategory_created_at'),
    ]

    operations = [
        migrations.RunPython(
            code=cleanup_and_add_categories,
            reverse_code=reverse_cleanup_and_add_categories
        ),
    ]