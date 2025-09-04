# -*- coding: utf-8 -*-
"""
Custom exceptions for the qreu email library.

Provides specific exception types for different email-related errors,
maintaining Python 2.7 and 3.x compatibility.
"""
from __future__ import absolute_import, unicode_literals


class QreuError(Exception):
    """Base exception class for all qreu-related errors."""
    pass


class EmailParsingError(QreuError):
    """Raised when there's an error parsing an email message."""
    
    def __init__(self, message, original_error=None):
        # type: (str, Exception) -> None
        super(EmailParsingError, self).__init__(message)
        self.original_error = original_error


class AddressError(QreuError):
    """Raised when there's an error with email address handling."""
    
    def __init__(self, message, invalid_address=None):
        # type: (str, str) -> None
        super(AddressError, self).__init__(message)
        self.invalid_address = invalid_address


class AttachmentError(QreuError):
    """Raised when there's an error with email attachments."""
    
    def __init__(self, message, filename=None):
        # type: (str, str) -> None
        super(AttachmentError, self).__init__(message)
        self.filename = filename


class SendError(QreuError):
    """Raised when there's an error sending an email."""
    
    def __init__(self, message, smtp_error=None):
        # type: (str, Exception) -> None
        super(SendError, self).__init__(message)
        self.smtp_error = smtp_error


class HeaderError(QreuError):
    """Raised when there's an error with email headers."""
    
    def __init__(self, message, header_name=None):
        # type: (str, str) -> None
        super(HeaderError, self).__init__(message)
        self.header_name = header_name