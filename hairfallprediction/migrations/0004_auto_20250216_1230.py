from django.db import migrations


def set_default_author(apps, schema_editor):
    Product = apps.get_model('hairfallprediction', 'Product')
    User = apps.get_model('auth', 'User')

    try:
        agent3 = User.objects.get(username='agent3')
        products_without_author = Product.objects.filter(author__isnull=True)
        for product in products_without_author:
            product.author = agent3
            product.save()
    except User.DoesNotExist:
        # Handle the case where agent3 doesn't exist
        pass


class Migration(migrations.Migration):
    dependencies = [
        ('hairfallprediction', '0003_product_author'),  # Make sure this matches your last migration
    ]

    operations = [
        migrations.RunPython(set_default_author),
    ]