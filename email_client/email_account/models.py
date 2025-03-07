from django.db import models

class EmailAccount(models.Model):
    email = models.EmailField(unique=True)  # Email address for login
    app_password = models.CharField(max_length=255)  # App password or email password (should be stored securely)
    imap_server = models.CharField(max_length=255)  # IMAP server (for receiving emails)

    # Track whether the email is currently active
    is_active = models.BooleanField(default=False)
    # Timestamp for when the email account was last checked
    last_checked = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email


class Email(models.Model):
    account = models.ForeignKey(EmailAccount, related_name="emails", on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    sender = models.EmailField()
    body = models.TextField()
    received_at = models.DateTimeField()
    is_checked = models.BooleanField(default=False)  # Track if the email has been processed/checked

    def __str__(self):
        return f"Subject: {self.subject} from {self.sender}"

