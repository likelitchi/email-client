from rest_framework import viewsets, generics
from .models import EmailAccount, Email
from .serializers import EmailSerializer, EmailAccountSerializer, EmailAccountAndEmailSerializer


class EmailAccountListView(generics.ListAPIView):
    queryset = EmailAccount.objects.all()
    serializer_class = EmailAccountSerializer


class ReceivedEmailViewSet(viewsets.ModelViewSet):
    queryset = Email.objects.all().order_by('-received_at')
    serializer_class = EmailSerializer


class EmailAccountAndAndEmailViewSet(viewsets.ModelViewSet):
    queryset = EmailAccount.objects.prefetch_related("emails").all()
    serializer_class = EmailAccountAndEmailSerializer
