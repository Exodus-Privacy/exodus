# Fix for issue #300: version names longer than 50 characters (e.g. flavor
# suffixed Play releases) make the Application save fail with a DataError
# after the "Tracker analysis: success" state, leaving the analysis stuck.
# Extend the field to 255 so long version names are stored.
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0015_application_app_name_trgm_idx'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='version',
            field=models.CharField(max_length=255),
        ),
    ]
