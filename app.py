import os

from flask import Flask, render_template, request, jsonify
import os
import smtplib
import ssl
from email.message import EmailMessage

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.post('/contact')
def contact():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    message = request.form.get('message', '').strip()

    if not name or not email or not message:
        # If the client expects JSON, return JSON; otherwise return an alert and go back.
        if "application/json" in request.headers.get("Accept", "").lower() or \
           request.headers.get("X-Requested-With", "").lower() == "xmlhttprequest":
            return jsonify({"ok": False, "error": "All fields are required."}), 400
        return (
            "<script>alert('All fields are required.'); window.location.href = '/';</script>",
            400,
            {"Content-Type": "text/html; charset=utf-8"},
        )

    try:
        send_email(
            subject=f"Contact form message from {name}",
            body=f"From: {name} <{email}>\n\n{message}",
            from_email=os.environ.get("SMTP_FROM", email),
            reply_to=email,
        )
        # If the client expects JSON (AJAX/fetch), return JSON; else show popup and redirect.
        if "application/json" in request.headers.get("Accept", "").lower() or \
           request.headers.get("X-Requested-With", "").lower() == "xmlhttprequest":
            return jsonify({"ok": True, "message": "Message sent successfully."}), 200
        return (
            "<script>alert('Message sent successfully.'); window.location.href = '/';</script>",
            200,
            {"Content-Type": "text/html; charset=utf-8"},
        )
    except Exception as e:
        # Log e in a real app
        if "application/json" in request.headers.get("Accept", "").lower() or \
           request.headers.get("X-Requested-With", "").lower() == "xmlhttprequest":
            return jsonify({"ok": False, "error": "Failed to send message."}), 500
        return (
            "<script>alert('Failed to send message. Please try again later.'); window.location.href = '/';</script>",
            500,
            {"Content-Type": "text/html; charset=utf-8"},
        )

def send_email(subject: str, body: str, from_email: str, reply_to: str = None):
    """
    Sends an email using SMTP settings from environment variables.

    Required/optional env vars:
      - SMTP_SERVER (e.g., smtp.gmail.com)
      - SMTP_PORT (e.g., 587 for STARTTLS, or 465 for SSL)
      - SMTP_USERNAME
      - SMTP_PASSWORD
      - SMTP_USE_SSL (optional: "1" for SSL, otherwise STARTTLS is used)
      - CONTACT_RECIPIENT (default: averaenterprisesinc@gnmail.com)
      - SMTP_FROM (optional: overrides From address)
    """
    smtp_server = os.environ.get("SMTP_SERVER")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USERNAME")
    smtp_pass = os.environ.get("SMTP_PASSWORD")
    use_ssl = os.environ.get("SMTP_USE_SSL", "").strip() == "1"
    recipient = os.environ.get("CONTACT_RECIPIENT", "averaenterprisesinc@gnmail.com")

    if not smtp_server or not smtp_user or not smtp_pass:
        raise RuntimeError("SMTP configuration is incomplete.")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_email or smtp_user
    msg["To"] = recipient
    if reply_to:
        msg["Reply-To"] = reply_to
    msg.set_content(body)

    if use_ssl:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
    else:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()
            server.starttls(context=ssl.create_default_context())
            server.ehlo()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)

if __name__ == '__main__':
    app.run(debug=True)