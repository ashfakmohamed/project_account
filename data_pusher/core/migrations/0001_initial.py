import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Account",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("account_id", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("account_name", models.CharField(max_length=255)),
                ("website", models.URLField(blank=True)),
                ("token_prefix", models.CharField(editable=False, max_length=24, unique=True)),
                ("token_hash", models.CharField(editable=False, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="Destination",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("url", models.URLField()),
                ("http_method", models.CharField(choices=[("POST", "POST")], default="POST", max_length=10)),
                ("headers", models.JSONField(blank=True, default=dict)),
                ("account", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="destinations", to="core.account")),
            ],
        ),
    ]
