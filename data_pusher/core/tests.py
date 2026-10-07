from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Account, Destination


@override_settings(
    DATA_PUSHER_ALLOWED_DESTINATION_HOSTS=["webhook.example.com"],
    DATA_PUSHER_REQUEST_TIMEOUT_SECONDS=3,
)
class ManagementApiTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="Strong-password-2026!",
        )

    def test_anonymous_user_cannot_list_accounts(self):
        response = self.client.get(reverse("account-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_is_returned_once_at_account_creation(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(
            reverse("account-list"),
            {
                "email": "owner@example.com",
                "account_name": "Example",
                "website": "https://example.com",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        raw_token = response.data["app_secret_token"]
        account = Account.objects.get()
        self.assertTrue(account.check_token(raw_token))
        self.assertNotEqual(account.token_hash, raw_token)

        detail = self.client.get(reverse("account-detail", args=[account.id]))
        self.assertNotIn("app_secret_token", detail.data)

    def test_destination_must_use_allowlisted_https_host(self):
        self.client.force_authenticate(self.admin)
        raw_token = Account.generate_token()
        account = Account(
            email="owner@example.com",
            account_name="Example",
        )
        account.set_token(raw_token)
        account.save()

        response = self.client.post(
            reverse("destination-list"),
            {
                "account": account.id,
                "url": "http://127.0.0.1/internal",
                "headers": {},
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


@override_settings(
    DATA_PUSHER_ALLOWED_DESTINATION_HOSTS=["webhook.example.com"],
    DATA_PUSHER_REQUEST_TIMEOUT_SECONDS=3,
)
class IncomingDataTests(APITestCase):
    def setUp(self):
        self.raw_token = Account.generate_token()
        self.account = Account(
            email="owner@example.com",
            account_name="Example",
        )
        self.account.set_token(self.raw_token)
        self.account.save()
        self.destination = Destination.objects.create(
            account=self.account,
            url="https://webhook.example.com/events",
            headers={"X-Source": "data-pusher"},
        )

    @patch("core.views.requests.post")
    def test_valid_token_forwards_payload_safely(self, post):
        post.return_value = Mock(status_code=202, ok=True)
        response = self.client.post(
            reverse("incoming-data"),
            {"event": "created"},
            format="json",
            HTTP_CL_X_TOKEN=self.raw_token,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["forwarded"], 1)
        post.assert_called_once_with(
            self.destination.url,
            json={"event": "created"},
            headers=self.destination.headers,
            timeout=3,
            allow_redirects=False,
        )

    def test_invalid_token_is_rejected(self):
        response = self.client.post(
            reverse("incoming-data"),
            {"event": "created"},
            format="json",
            HTTP_CL_X_TOKEN="invalid.token",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
