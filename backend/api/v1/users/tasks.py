from celery import shared_task
from django.core.mail import send_mail, send_mass_mail


@shared_task(name='send_mail', ignore_result=True)
def send_mail_via_celery(
    subject,
    message,
    from_email,
    recipient_list,
    fail_silently=False,
    auth_user=None,
    auth_password=None,
    connection=None,
    html_message=None,
):
    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        fail_silently=False,
        auth_user=None,
        auth_password=None,
        connection=None,
        html_message=None,
    )


@shared_task(name='mass_send_mail', ignore_result=True)
def send_mass_mail_via_celery(
    datatuple,
    fail_silently=False,
    auth_user=None,
    auth_password=None,
    connection=None,
):
    send_mass_mail(
        datatuple,
        fail_silently=False,
        auth_user=None,
        auth_password=None,
        connection=None,
    )
