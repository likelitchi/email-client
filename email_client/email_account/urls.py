from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReceivedEmailViewSet, EmailAccountListView, EmailAccountAndAndEmailViewSet

router = DefaultRouter()
# router.register(r'email-accounts', EmailAccountViewSet)  # ✅ This is a ViewSet
router.register(r'received-emails', ReceivedEmailViewSet)  # ✅ This is also a ViewSet

urlpatterns = [
    path('', include(router.urls)),  # ✅ Includes ViewSet-based URLs
    path("email-accounts/", EmailAccountListView.as_view(), name="email-accounts"),  # ✅ Adds ListAPIView URL
    path("emails/", EmailAccountAndAndEmailViewSet.as_view({'get': 'list'}), name="emails"),  # ✅ Adds ListAPIView URL
]
