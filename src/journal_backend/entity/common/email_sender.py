from email.message import EmailMessage

import aiosmtplib

from journal_backend.config import SMTPConfig


class EmailSender:
    async def send_email(self, email_to: str, smtp_cfg: SMTPConfig, em: EmailMessage):
        async with aiosmtplib.SMTP(hostname=smtp_cfg.host, port=smtp_cfg.port, use_tls=True) as smtp:
            await smtp.login(smtp_cfg.email, smtp_cfg.password)
            await smtp.sendmail(
                smtp_cfg.email,
                email_to,
                em.as_string()
            )
