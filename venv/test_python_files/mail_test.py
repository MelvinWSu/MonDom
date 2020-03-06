#https://pythonhosted.org/Flask-Mail/
#Simple implementation of sending emails
from flask import Flask
from flask_mail import Mail
import os
from flask_mail import Message

app = Flask(__name__)

mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": os.environ['EMAIL_USER'],
    "MAIL_PASSWORD": os.environ['EMAIL_PASSWORD']
}

app.config.update(mail_settings)
mail = Mail(app)

if __name__ == "__main__":
    msg = Message(subject="Hello",
                  sender=app.config.get('MAIL_USERNAME'),
                  recipients=["msu009@ucr.edu"])
    with app.app_context():
        mail.send(msg)