# Generated manually for adding customer phone field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0007_add_service_ordering'),
    ]

    operations = [
        migrations.AddField(
            model_name='serviceorder',
            name='customer_phone',
            field=models.CharField(
                default='',
                help_text='Customer phone number (9 digits starting with 5, or 10 digits starting with 05)',
                max_length=10,
                verbose_name='Customer Phone'
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='serviceorder',
            name='customer_id',
            field=models.CharField(
                help_text='Customer identification number (10 digits)',
                max_length=10,
                verbose_name='Customer ID'
            ),
        ),
        migrations.AlterField(
            model_name='serviceorder',
            name='customer_image',
            field=models.ImageField(
                blank=True,
                help_text='Customer personal image (required)',
                null=True,
                upload_to='service_orders/customer_images/',
                verbose_name='Customer Image'
            ),
        ),
    ]
