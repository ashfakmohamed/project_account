from urllib.parse import urlsplit

from django.conf import settings
from rest_framework import serializers

from .models import Account, Destination


def validate_destination_url(value):
    parsed = urlsplit(value)
    hostname = (parsed.hostname or "").lower()
    allowed_hosts = {host.lower() for host in settings.DATA_PUSHER_ALLOWED_DESTINATION_HOSTS}

    if parsed.scheme != "https":
        raise serializers.ValidationError("Destination URLs must use HTTPS.")
    if not hostname or hostname not in allowed_hosts:
        raise serializers.ValidationError("Destination host is not allowlisted.")
    if parsed.username or parsed.password:
        raise serializers.ValidationError("Credentials are not allowed in destination URLs.")
    return value


class AccountSerializer(serializers.ModelSerializer):
    app_secret_token = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = (
            "id",
            "email",
            "account_id",
            "account_name",
            "website",
            "app_secret_token",
        )
        read_only_fields = ("id", "account_id", "app_secret_token")

    def create(self, validated_data):
        raw_token = Account.generate_token()
        account = Account(**validated_data)
        account.set_token(raw_token)
        account.save()
        account._issued_token = raw_token
        return account

    def get_app_secret_token(self, instance):
        return getattr(instance, "_issued_token", None)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data.get("app_secret_token") is None:
            data.pop("app_secret_token", None)
        return data


class DestinationSerializer(serializers.ModelSerializer):
    url = serializers.URLField(validators=[validate_destination_url])

    class Meta:
        model = Destination
        fields = ("id", "account", "url", "http_method", "headers")
        read_only_fields = ("id", "http_method")

    def validate_headers(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Headers must be a JSON object.")
        blocked = {"host", "content-length", "transfer-encoding"}
        if any(str(key).lower() in blocked for key in value):
            raise serializers.ValidationError("One or more headers are not allowed.")
        return value
