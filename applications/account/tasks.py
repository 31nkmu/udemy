from decouple import config
from django.core.mail import send_mail

from config.celery import app


@app.task
def send_user_activation_link(email, activation_code):
    full_link = f'http://{config("ALLOWED_HOSTS").split(",")[1]}:{config("MAIN_PORT")}/api/v1/account/activate/{activation_code}'
    send_mail(
        'from udemy',
        f'Your activation link {full_link}',
        config('EMAIL_HOST_USER'),
        [email]
    )


@app.task
def send_change_password_code(email, confirm_code):
    send_mail(
        'from udemy',
        f'Your confirm code {confirm_code}',
        config('EMAIL_HOST_USER'),
        [email]
    )
