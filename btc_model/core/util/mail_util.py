
import smtplib
import logging
from email.mime.text import MIMEText
from btc_model.setting.setting import get_settings

mail_host = get_settings('mail.host')
mail_user = get_settings('mail.user')
mail_pass = get_settings('mail.password')
sender = get_settings('mail.sender')
receivers = get_settings('mail.receivers')


def send_mail(subject, content=""):
    logging.info("发送邮件：%s %s", subject, content)
    try:
        message = MIMEText(content, 'plain', 'utf-8')
        message['From'] = sender
        message['To'] = ','.join(['<' + r + '>' for r in receivers])
        message['Subject'] = subject

        mailer = smtplib.SMTP_SSL(mail_host, port=465, timeout=10)
        mailer.connect(mail_host, 465)
        mailer.login(mail_user, mail_pass)
        mailer.sendmail(sender, receivers, message.as_string())
        mailer.quit()
    except Exception as e:
        logging.error(f"发送邮件失败, 错误信息: {e}", exc_info=True)
