# coding=utf-8
from __future__ import absolute_import

import email
from email.header import decode_header
import re

from flanker.addresslib import address


RE_PATTERNS = re.compile('\s*({0})'.format('|'.join(
    [
        'SV:',
        'Antw:',
        'VS:',
        'RE:',
        'AW:',
        'Vá:',
        'R:'
        'RIF:',
        'SV:',
        'BLS:',
        'Odp:',
        'YNT:'
    ])), re.IGNORECASE)


FW_PATTERNS = re.compile('\s*({0})'.format('|'.join(
    [
        'VS:',
        'Doorst:',
        'VL:',
        'TR:',
        'WG:',
        'Továbbítás:',
        'I:',
        'FS:',
        'VB:',
        'RV:',
        'ENC:',
        'PD:',
        'İLT'
    ])), re.IGNORECASE)


class Email(object):
    """
    Correu object

    :param raw_message: Raw string message
    """
    def __init__(self, raw_message):
        self.email = email.message_from_string(raw_message)

    def header(self, header, default=None):
        """
        Get the email Header always in Unicode

        :param header: Header string
        :param default: Default result if header is not found
        :return: Header value
        """
        result = []
        header_value = self.email.get(header, default)
        if header_value:
            for part in decode_header(header_value):
                if part[1]:
                    result.append(part[0].decode(part[1]))
                else:
                    result.append(part[0])
            header_value =  ''.join(result)
        return header_value

    @property
    def is_reply(self):
        """
        Property to know if this message is a reply or not.

        Conditions: Is not forwarded,  has header 'In-Reply-To' or subject
        matches with a 'RE' pattern.
        https://en.wikipedia.org/wiki/List_of_email_subject_abbreviations
        :return: bool
        """
        return (not self.is_forwarded and (
            bool(self.header('In-Reply-To'))
                or bool(re.match(RE_PATTERNS, self.header('Subject', '')))
        ))

    @property
    def is_forwarded(self):
        """
        Use Forward expressions in the subject to check

        https://en.wikipedia.org/wiki/List_of_email_subject_abbreviations
        :return: bool
        """
        return bool(re.match(FW_PATTERNS, self.header('Subject', '')))

    @property
    def subject(self):
        """
        Clean subject without abbreviations
        :return: str
        """
        subject = re.sub(RE_PATTERNS, '', self.header('Subject', ''))
        subject = re.sub(FW_PATTERNS, '', subject)
        return subject.strip()

    @property
    def references(self):
        """
        List of email references
        :return: list
        """
        return self.header('References', '').split()

    @property
    def parent(self):
        """
        Parent Message-Id
        :return: str
        """
        return self.references and self.references[-1] or None

    def __nonzero__(self):
        return bool(self.email)

    def __bool__(self):
        return self.__nonzero__()

    @property
    def from_(self):
        """

        :return: `flanker.addresslib.address.Address`
        """
        return address.parse(self.header('From', ''))

    @property
    def to(self):
        """

        :return: `flanker.addresslib.address.AddressList`
        """
        return address.parse_list(self.header('To', ''))

    @property
    def cc(self):
        """
        :return: `flanker.addresslib.address.AddressList`
        """
        return address.parse_list(self.header('Cc', ''))

    @property
    def bcc(self):
        """
        :return: `flanker.addresslib.address.AddressList`
        """
        return address.parse_list(self.header('Bcc', ''))

    @property
    def recipients(self):
        return self.to + self.cc + self.bcc
