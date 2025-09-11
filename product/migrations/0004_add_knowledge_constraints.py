# Generated migration for knowledge base constraints

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0003_add_knowledge_base_models'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='knowledgearticle',
            unique_together={('company', 'title')},
        ),
    ]
