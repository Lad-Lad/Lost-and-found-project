from threading import Thread
from flask import render_template
from flask_mail import Message
from app import app, mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[Campus Lost & Found] Reset Your Password', 
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))


def send_item_confirmation_email(user, item):
    send_email(f'[Campus Lost & Found] Your {item.item_type.capitalize()} Item Posted!', 
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/item_confirmation.txt',
                                         user=user, item=item),
               html_body=render_template('email/item_confirmation.html',
                                         user=user, item=item))