from django.urls import path
from .views import (
    AccountListCreateView,
    AccountRetrieveUpdateDestroyView,
    DestinationListCreateView,
    DestinationRetrieveUpdateDestroyView,
    incoming_data,
    Api
)

urlpatterns = [
    path('accounts/', AccountListCreateView.as_view(), name='account-list-create'),
    path('accounts/<int:pk>/', AccountRetrieveUpdateDestroyView.as_view(), name='account-retrieve-update-destroy'),
    path('destinations/', DestinationListCreateView.as_view(), name='destination-list-create'),
    path('destinations/<int:pk>/', DestinationRetrieveUpdateDestroyView.as_view(), name='destination-retrieve-update-destroy'),
    path('server/incoming_data/', incoming_data, name='incoming-data'),
        path('core/',Api.as_view(),name="all_request")
]
