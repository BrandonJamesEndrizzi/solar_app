"""Send the assembled report over SMTP."""

import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from settings import load_config, require_env


def _smtp_settings():
    """Return (host, port, use_ssl) from the [SMTP] section of config.ini."""
    config = load_config()
    host = config.get("SMTP", "host", fallback="smtp.gmail.com")
    port = config.getint("SMTP", "port", fallback=465)
    use_ssl = config.getboolean("SMTP", "use_ssl", fallback=True)
    return host, port, use_ssl


def _connect():
    host, port, use_ssl = _smtp_settings()
    if use_ssl:
        return smtplib.SMTP_SSL(host, port)

    smtp = smtplib.SMTP(host, port)
    smtp.starttls()
    return smtp


def _build_message(subject, to_email, from_email):
    message = MIMEMultipart("related")
    message["Subject"] = subject
    message["From"] = from_email
    message["To"] = to_email
    return message


def _attach_inline_image(message, image_path, image_cid):
    with open(image_path, "rb") as image_file:
        image = MIMEImage(image_file.read())
    image.add_header("Content-ID", f"<{image_cid}>")
    image.add_header("Content-Disposition", "inline")
    message.attach(image)


def _attach_file(message, attachment_path):
    filename = os.path.basename(str(attachment_path))
    with open(attachment_path, "rb") as attachment_file:
        part = MIMEApplication(attachment_file.read(), Name=filename)
    part["Content-Disposition"] = f'attachment; filename="{filename}"'
    message.attach(part)


def send_email(subject, html_body, to_email, attachment_paths=(), image_path=None,
               image_cid=None):
    """Send an HTML email with optional inline image and file attachments."""
    email_address = require_env("EMAIL_ADDRESS")
    email_password = require_env("EMAIL_PASSWORD")

    message = _build_message(subject, to_email, email_address)
    message.attach(MIMEText(html_body, "html"))

    if image_path and image_cid and os.path.isfile(image_path):
        _attach_inline_image(message, image_path, image_cid)

    for attachment_path in attachment_paths:
        if os.path.isfile(attachment_path):
            _attach_file(message, attachment_path)

    try:
        with _connect() as smtp:
            smtp.login(email_address, email_password)
            smtp.send_message(message)
    except (smtplib.SMTPException, OSError) as err:
        print(f"Failed to send email to {to_email}: {err}")
        return False

    print(f"Email sent to {to_email}")
    return True
