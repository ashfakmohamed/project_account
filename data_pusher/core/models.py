import secrets
import uuid

from django.contrib.auth.hashers import check_password, make_password
from django.db import models


class Account(models.Model):
    email = models.EmailField(unique=True)
    account_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    account_name = models.CharField(max_length=255)
    website = models.URLField(blank=True)
    token_prefix = models.CharField(max_length=24, unique=True, editable=False)
    token_hash = models.CharField(max_length=255, editable=False)

    @staticmethod
    def generate_token():
        prefix = secrets.token_hex(6)
        return f"{prefix}.{secrets.token_urlsafe(32)}"

    def set_token(self, raw_token):
        self.token_prefix = raw_token.partition(".")[0]
        self.token_hash = make_password(raw_token)

    def check_token(self, raw_token):
        return check_password(raw_token, self.token_hash)

    def __str__(self):
        return self.account_name


class Destination(models.Model):
    class Method(models.TextChoices):
        POST = "POST", "POST"

    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="destinations",
    )
    url = models.URLField()
    http_method = models.CharField(
        max_length=10,
        choices=Method.choices,
        default=Method.POST,
    )
    headers = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.account.account_name}: {self.url}"
