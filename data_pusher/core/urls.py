from rest_framework.routers import DefaultRouter

from .views import AccountViewSet, DestinationViewSet

router = DefaultRouter()
router.register("accounts", AccountViewSet, basename="account")
router.register("destinations", DestinationViewSet, basename="destination")

urlpatterns = router.urls
