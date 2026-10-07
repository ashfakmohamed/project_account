from collections.abc import Mapping

import requests
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from django.conf import settings

from .models import Account, Destination
from .serializers import (
    AccountSerializer,
    DestinationSerializer,
    validate_destination_url,
)


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all().order_by("account_name", "id")
    serializer_class = AccountSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, methods=["post"], url_path="rotate-token")
    def rotate_token(self, request, pk=None):
        account = self.get_object()
        raw_token = Account.generate_token()
        account.set_token(raw_token)
        account.save(update_fields=["token_prefix", "token_hash"])
        return Response({"app_secret_token": raw_token})


class DestinationViewSet(viewsets.ModelViewSet):
    queryset = Destination.objects.select_related("account").all().order_by("id")
    serializer_class = DestinationSerializer
    permission_classes = [IsAdminUser]


class IncomingDataView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "incoming"

    def post(self, request):
        raw_token = request.headers.get("CL-X-TOKEN", "")
        prefix, separator, _secret = raw_token.partition(".")
        if not separator or not prefix:
            return Response(
                {"error": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        account = Account.objects.filter(token_prefix=prefix).first()
        if account is None or not account.check_token(raw_token):
            return Response(
                {"error": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not isinstance(request.data, Mapping):
            return Response(
                {"error": "The request body must be a JSON object."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payload = dict(request.data)
        results = []
        for destination in account.destinations.all():
            try:
                validate_destination_url(destination.url)
                response = requests.post(
                    destination.url,
                    json=payload,
                    headers=destination.headers,
                    timeout=settings.DATA_PUSHER_REQUEST_TIMEOUT_SECONDS,
                    allow_redirects=False,
                )
                results.append(
                    {
                        "destination_id": destination.id,
                        "status_code": response.status_code,
                        "ok": response.ok,
                    }
                )
            except (requests.RequestException, ValueError):
                results.append(
                    {
                        "destination_id": destination.id,
                        "status_code": None,
                        "ok": False,
                    }
                )

        return Response(
            {
                "account_id": str(account.account_id),
                "forwarded": sum(1 for result in results if result["ok"]),
                "results": results,
            },
            status=status.HTTP_200_OK,
        )
