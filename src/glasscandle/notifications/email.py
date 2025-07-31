"""Email notification functionality."""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional
import os


def send_email(
    subject: str,
    body: str,
    smtp_config: Optional[Dict[str, str]] = {}
) -> None:
    """Send an email notification.
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body content
        smtp_config: SMTP configuration dictionary containing:
            - smtp_server: SMTP server hostname
            - smtp_port: SMTP server port
            - username: SMTP username
            - password: SMTP password
            - from: Sender email address (optional, defaults to username)
    """
    smtp_config = {
        "to": smtp_config.get("to") or os.getenv("EMAIL_TO"),
        "from": smtp_config.get("from") or os.getenv("EMAIL_FROM"),
        "smtp_server": smtp_config.get("smtp_server") or os.getenv("EMAIL_SMTP_SERVER"),
        "smtp_port": int(smtp_config.get("smtp_port") or os.getenv("EMAIL_SMTP_PORT", "587")),
        "username": smtp_config.get("username") or os.getenv("EMAIL_USERNAME"),
        "password": smtp_config.get("password") or os.getenv("EMAIL_PASSWORD"),
    }
    if not smtp_config.get("to") or not smtp_config.get("username") or not smtp_config.get("password"):
        raise ValueError("Missing required email configuration: to, username, and password must be set.")

    from_email = smtp_config.get("from", smtp_config["username"])
    to = smtp_config["to"]
    
    # Create message
    message = MIMEMultipart()
    message["From"] = from_email
    message["To"] = to
    message["Subject"] = subject
    
    # Add body to email
    message.attach(MIMEText(body, "plain"))
    
    # Create secure connection and send email
    try:
        # Create SSL context
        context = ssl.create_default_context()
        
        # Connect to server
        with smtplib.SMTP(smtp_config["smtp_server"], smtp_config["smtp_port"]) as server:
            server.starttls(context=context)
            server.login(smtp_config["username"], smtp_config["password"])
            
            # Send email
            text = message.as_string()
            server.sendmail(from_email, to, text)
            
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")
        raise
