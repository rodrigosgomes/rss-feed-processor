import sys
sys.path.append('src')
from config.settings import EMAIL_SETTINGS, recipient_email
print('=== Environment Variables Test ===')
print(f'SMTP Server: {EMAIL_SETTINGS.get("smtp_server", "NOT FOUND")}')
print(f'Sender Email: {EMAIL_SETTINGS.get("sender_email", "NOT FOUND")}')
print(f'Recipient Email: {recipient_email}')
print(f'SMTP Port: {EMAIL_SETTINGS.get("smtp_port", "NOT FOUND")}')
print(f'Password length: {len(EMAIL_SETTINGS.get("sender_password", "")) if EMAIL_SETTINGS.get("sender_password") else 0} characters')
