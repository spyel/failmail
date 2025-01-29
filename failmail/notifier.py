# Copyright (c) 2025 Spyel
# Licensed under the MIT License. See LICENSE file for details.
import smtplib
import logging
import datetime
import traceback
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from .registry import ExceptionRegistry, RegistryEntry, Context, BodyTypes

logger = logging.getLogger(__name__)


class ExceptionNotifier:
    """Notify recipients via email when exceptions occur."""

    def __init__(
        self,
        host: tuple[str, int],
        sender_email: str,
        credentials: tuple[str, str] | None = None,
        encryption: str = 'tls'
    ) -> None:
        self.host, self.port = host
        self.sender_email: str = sender_email
        self.credentials: tuple[str, str] | None = credentials
        self.encryption: str = encryption
        self.registry: ExceptionRegistry = ExceptionRegistry()

    def register_exception(
        self,
        exception_type: type[Exception],
        recipients: list[str],
        subject: str,
        body: str,
        body_type: BodyTypes = 'plain'
    ) -> None:
        """
        Registers a new notification entry for a specific exception type.

        :param exception_type: The exception type to associate with this entry.
        :param recipients: A list of recipient email addresses.
        :param subject: The email subject template.
        :param body: The email body template.
        :param body_type: The type of the body, either 'plain' or 'html'.
        """
        self.registry.register(exception_type, recipients, subject, body, body_type)

    def notify(self, exception: Exception, additional_context: Context | None = None) -> None:
        """
        Notify recipients about an exception.

        :param exception: The exception instance to notify about.
        :param additional_context: The context to format the subject and body.
        """
        exception_type: type[Exception] = type(exception)
        entries: list[RegistryEntry] = self.registry.get_entries(exception_type)

        if not entries:
            return

        default_context: Context = {
            'error_type': exception_type.__name__,
            'error_message': str(exception),
            'error_traceback': traceback.format_exc(),
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        context: Context = default_context | (additional_context or {})

        for entry in entries:
            self._send_notification(entry, context)

    def _send_notification(self, entry: RegistryEntry, context: Context) -> None:
        subject, body = entry.format(context)

        message = MIMEMultipart()
        message['From'] = self.sender_email
        message['To'] = ', '.join(entry.recipients)
        message['Subject'] = subject
        message.attach(MIMEText(body, entry.body_type))

        try:
            with self._get_connection() as connection:
                if self.credentials:
                    connection.login(self.credentials[0], self.credentials[1])
                connection.send_message(message)
                logger.info(f'Notification sent to: {', '.join(entry.recipients)}')
        except smtplib.SMTPException as e:
            logger.error(f'Failed to send notification to {', '.join(entry.recipients)}: {e}', exc_info=True)

    def _get_connection(self) -> smtplib.SMTP:
        try:
            if self.encryption == 'ssl':
                return smtplib.SMTP_SSL(self.host, self.port)
            connection = smtplib.SMTP(self.host, self.port)
            if self.encryption == 'tls':
                connection.starttls()
            return connection
        except smtplib.SMTPException as e:
            logger.error(f'Failed to establish connection to SMTP server: {e}', exc_info=True)
            raise
