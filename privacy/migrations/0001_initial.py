from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [migrations.CreateModel(name='Consent', fields=[
        ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
        ('value', models.CharField(choices=[('yes','yes'),('no','no')], max_length=3)),
        ('withdrawn', models.BooleanField(default=False)),
    ])]
