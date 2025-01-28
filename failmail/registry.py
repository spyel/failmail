# Copyright (c) 2025 Spyel
# Licensed under the MIT License. See LICENSE file for details.
from collections import defaultdict
from typing import Any, Literal
from string import Template

BodyTypes = Literal['plain', 'html']
Context = dict[str, Any]


class RegistryEntry:
    """
    Represents an email notification entry for the exception registry.
    """

    def __init__(
        self,
        recipients: list[str],
        subject: str,
        body: str,
        body_type: BodyTypes
    ) -> None:
        if not recipients or not all(isinstance(r, str) for r in recipients):
            raise ValueError('Recipients must be a non-empty list of strings.')

        if not isinstance(subject, str) or not subject.strip():
            raise ValueError('Subject must be a non-empty string.')

        if not isinstance(body, str) or not body.strip():
            raise ValueError('Body must be a non-empty string.')

        if body_type not in ('plain', 'html'):
            raise ValueError(f'Invalid body_type \'{body_type}\'. Expected \'plain\' or \'html\'.')

        self.recipients: list[str] = recipients
        self.subject: str = subject
        self.body: str = body
        self.body_type: BodyTypes = body_type

    def format(self, context: Context) -> tuple[str, str]:
        """
        Formats the subject and body of the entry using the provided context.

        :param context: A dictionary of values to substitute in the templates.
        :return: A tuple containing the formatted subject and body.
        """
        subject = Template(self.subject).safe_substitute(context)
        body = Template(self.body).safe_substitute(context)
        return subject, body


class ExceptionRegistry:
    """
    Manages a registry of exceptions and their associated notification entries.
    """

    def __init__(self) -> None:
        self.registry: dict[type[Exception], list[RegistryEntry]] = defaultdict(list)

    def register(
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
        entry: RegistryEntry = RegistryEntry(recipients, subject, body, body_type)
        self.registry[exception_type].append(entry)

    def get_entries(self, exception_type: type[Exception]) -> list[RegistryEntry]:
        """
        Retrieves all registry entries for the given exception type, including
        entries for base exception classes if none are registered specifically.

        :param exception_type: The exception type to look up.
        """
        while exception_type:
            if exception_type in self.registry:
                return self.registry[exception_type]
            exception_type = exception_type.__base__
        return []
