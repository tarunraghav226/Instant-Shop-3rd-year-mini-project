from django.core.mail import send_mail
from InstantShop import settings

def mail(email, firstname, link):
    link = 'http://instantshop.pythonanywhere.com/verify-email/' + link
    subject = 'Email Verification Mail.'
    message = 'Dear {0},\n\t\tCongratulations, you have succesfully registerd to InstantShop.\nBelow is the link to verify your email. Click it to verify your mail.\n{1}'.format(firstname,link)
    recepient = email
    send_mail(subject, 
        message, settings.EMAIL_HOST_USER, [recepient], fail_silently = False)
