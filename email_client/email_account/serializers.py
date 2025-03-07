from rest_framework import serializers
from .models import EmailAccount, Email


class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Email
        fields = '__all__'


class EmailAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailAccount
        fields = ["id", "email"]


class EmailAccountAndEmailSerializer(serializers.ModelSerializer):
    emails = EmailSerializer(many=True, read_only=True)  # Include emails in response

    class Meta:
        model = EmailAccount
        fields = ["email", "emails"]  # Return grouped emails

