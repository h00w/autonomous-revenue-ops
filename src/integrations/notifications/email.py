from __future__ import annotations

import smtplib
import ssl
from email.message import EmailMessage as MIMEEmailMessage
from typing import Any, Callable

from ..errors import IntegrationError, IntegrationErrorKind
from ..models import EmailMessage, NotificationResult

SMTPFactory = Callable[..., Any]


class SMTPEmailAdapter:
    """Bounded SMTP adapter for transactional outreach delivery.

    Provider-specific Gmail/Workspace OAuth can replace this adapter later
    without changing the EmailMessage contract.
    """

    provider = "smtp"

    def __init__(
        self,
        *,
        host: str,
        port: int,
        from_email: str,
        username: str | None = None,
        password: str | None = None,
        use_starttls: bool = True,
        timeout_seconds: float = 10.0,
        smtp_factory: SMTPFactory = smtplib.SMTP,
    ) -> None:
        if not host:
            raise ValueError("SMTP host is required")
        if not from_email:
            raise ValueError("SMTP from_email is required")
        self.host = host
        self.port = port
        self.from_email = from_email
        self.username = username
        self.password = password
        self.use_starttls = use_starttls
        self.timeout_seconds = timeout_seconds
        self.smtp_factory = smtp_factory

    def send(self, message: EmailMessage) -> NotificationResult:
        mime = MIMEEmailMessage()
        mime["From"] = self.from_email
        mime["To"] = str(message.to)
        mime["Subject"] = message.subject
        if message.reply_to:
            mime["Reply-To"] = str(message.reply_to)
        mime.set_content(message.text)

        try:
            with self.smtp_factory(self.host, self.port, timeout=self.timeout_seconds) as smtp:
                if self.use_starttls:
                    smtp.starttls(context=ssl.create_default_context())
                if self.username:
                    smtp.login(self.username, self.password or "")
                result = smtp.send_message(mime)
        except smtplib.SMTPAuthenticationError as exc:
            raise IntegrationError(
                provider=self.provider,
                kind=IntegrationErrorKind.AUTHENTICATION,
                message="SMTP authentication failed",
                retryable=False,
                status_code=getattr(exc, "smtp_code", None),
                details=str(exc),
            ) from exc
        except (smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected, TimeoutError, OSError) as exc:
            raise IntegrationError(
                provider=self.provider,
                kind=IntegrationErrorKind.NETWORK,
                message="SMTP transport failure",
                retryable=True,
                details=str(exc),
            ) from exc
        except smtplib.SMTPException as exc:
            raise IntegrationError(
                provider=self.provider,
                kind=IntegrationErrorKind.PROVIDER,
                message="SMTP provider rejected the message",
                retryable=False,
                details=str(exc),
            ) from exc

        delivered = not bool(result)
        if not delivered:
            raise IntegrationError(
                provider=self.provider,
                kind=IntegrationErrorKind.PROVIDER,
                message="SMTP server refused one or more recipients",
                retryable=False,
                details=result,
            )
        return NotificationResult(provider=self.provider, delivered=True)

    def close(self) -> None:
        return None
