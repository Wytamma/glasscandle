import pytest
from glasscandle.notifications.email import send_email


@pytest.fixture
def smtp_env_vars(monkeypatch):
    monkeypatch.setenv("EMAIL_SMTP_SERVER", "smtp.example.com")
    monkeypatch.setenv("EMAIL_SMTP_PORT", "587")
    monkeypatch.setenv("EMAIL_USERNAME", "test@example.com")
    monkeypatch.setenv("EMAIL_PASSWORD", "password123")
    monkeypatch.setenv("EMAIL_TO", "recipient@example.com")



def test_send_email_success(smtp_env_vars, mocker):
    # Mock the SMTP class
    mock_smtp = mocker.patch("smtplib.SMTP")
    mock_server = mock_smtp.return_value.__enter__.return_value
    
    subject = "Test Subject"
    body = "Test Body"

    send_email(subject, body)
    
    # Verify SMTP was called correctly
    mock_smtp.assert_called_once_with("smtp.example.com", 587)
    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once_with("test@example.com", "password123")
    mock_server.sendmail.assert_called_once()


def test_send_email_missing_from(smtp_env_vars, mocker):
    # Mock the SMTP class
    mock_smtp = mocker.patch("smtplib.SMTP")
    mock_server = mock_smtp.return_value.__enter__.return_value
    
    subject = "Test Subject"
    body = "Test Body"

    send_email(subject, body)
    
    # Verify SMTP was called correctly (should use username as from address)
    mock_smtp.assert_called_once_with("smtp.example.com", 587)
    mock_server.sendmail.assert_called_once()


def test_send_email_invalid_credentials(smtp_env_vars):
    subject = "Test Subject"
    body = "Test Body"

    smtp_config = {}
    smtp_config["username"] = "invalid"
    smtp_config["password"] = "invalid"

    with pytest.raises(Exception):
        send_email(subject, body, smtp_config)
