import imaplib
import email
import smtplib
from email.header import decode_header

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import parsedate_to_datetime

from email_account.models import EmailAccount, Email

from celery import shared_task

EMAIL_ACCOUNTS = [
    {
        "email": "ivanli.hktvmall@gmail.com",
        "password": "aibhqbhtwjnqpvkc",
        "imap_server": "imap.gmail.com",
    },
    # Add more accounts here
]

SPECIAL_KEYWORDS = ["test"]  # Customize your keywords

# Email alert configuration
SMTP_SERVER = "smtp.gmail.com"  # Change if you're using a different email provider
SMTP_PORT = 587  # For Gmail
SMTP_USERNAME = "ivanli.hktvmall@gmail.com"  # Your email address
SMTP_PASSWORD = "aibhqbhtwjnqpvkc"  # Your email account password or app password
ALERT_EMAIL = "ivanli.hktvmall@gmail.com"  # The email where you want to receive alerts

# Send email alert function
def send_email_alert(subject):
    """Send an email alert with the subject of the special email."""
    try:
        # Create the email content
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = ALERT_EMAIL
        msg['Subject'] = f"ALERT: Special email found with subject: {subject}"

        # The body of the email
        body = f"A special email was found with the subject: {subject}"
        msg.attach(MIMEText(body, 'plain'))

        # Set up the server and send the email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Secure the connection
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(SMTP_USERNAME, ALERT_EMAIL, text)
        server.quit()

        print(f"Sent alert email to {ALERT_EMAIL}")

    except Exception as e:
        print(f"❌ Error sending email alert: {e}")


def extract_email_body(msg):
    """Extract the plain text or HTML content from an email message."""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            # Extract text/plain or text/html, ignoring attachments
            if "attachment" not in content_disposition:
                if content_type == "text/plain":
                    return part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8")
                elif content_type == "text/html":
                    return part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8")
    else:
        # If it's not multipart, get the payload directly
        return msg.get_payload(decode=True).decode(msg.get_content_charset() or "utf-8")

    return None  # Default case if no text is found

@shared_task
def check_emails():
    print("Checking emails...")

    accounts = EmailAccount.objects.filter(is_active=True)

    if accounts is None:
        print("No account in database!")

    for account in accounts:
        try:
            print(f"🔄 Checking emails for {account.email}...")
            mail = imaplib.IMAP4_SSL(account.imap_server)
            mail.login(account.email, account.app_password)
            mail.select("INBOX")  # Ensure we are checking only the main mailbox

            # Search for the newest unread email
            result, data = mail.search(None, "UNSEEN")  # Only get unread emails
            print(data)

            email_ids = data[0].split()

            if not email_ids:
                print("✅ No unread emails found.")
                mail.logout()
                continue  # Skip to the next account if no unread emails

            newest_email_id = email_ids[-1]  # Get the latest unread email

            # Fetch the newest unread email
            result, msg_data = mail.fetch(newest_email_id, "(RFC822)")
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            # Decode subject
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or "utf-8")

            print(f"📧 Newest Email Subject: {subject}")

            # Check if subject contains special keywords
            if any(keyword.lower() in subject.lower() for keyword in SPECIAL_KEYWORDS):
                print(f"🔍 Found a special email with keyword: {subject}")

                email_date_str = msg["Date"]  # Example: "Wed, 26 Feb 2025 10:44:19 +0800"

                try:
                    # Convert email date to a proper datetime object
                    email_datetime = parsedate_to_datetime(email_date_str)

                    # Format it properly for Django (YYYY-MM-DD HH:MM:SS)
                    formatted_date = email_datetime.strftime("%Y-%m-%d %H:%M:%S")

                    print(f"✅ Formatted Date: {formatted_date}")  # Debugging

                    # Store email in database
                    Email.objects.create(
                        account=account,
                        subject=subject,
                        sender=msg["From"],
                        body=extract_email_body(msg),
                        received_at=formatted_date,
                        is_checked=False
                    )
                except Exception as e:
                    print(f"❌ Date Parsing Error: {e}")

            else:
                print(f"⚠️ Email does not contain any special keywords.")

            mail.logout()

        except Exception as e:
            print(f"❌ Error checking emails: {e}")
