from rest_framework.routers import DefaultRouter

from .views import SessionViewSet, SpeakerViewSet

router = DefaultRouter()
router.register(r"sessions", SessionViewSet, basename="session")
router.register(r"speakers", SpeakerViewSet, basename="speaker")

urlpatterns = router.urls
