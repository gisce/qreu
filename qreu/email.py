# coding=utf-8
from __future__ import absolute_import, unicode_literals

import email
from email.encoders import encode_base64
from email.header import decode_header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from html2text import html2text

import re

from qreu import address


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
    def __init__(self, **kwargs):
        self.email = MIMEMultipart()
        to_address = kwargs.get('to', False)
        if to_address:
            if isinstance(to_address, list):
                to_address = ','.join(to_address)
            self.email['To'] = to_address
        subject = kwargs.get('subject', False)
        if subject:
            self.email['Subject'] = subject
        from_address = kwargs.get('from', False)
        if from_address:
            self.email['From'] = from_address
        cc_address = kwargs.get('cc', False)
        if cc_address:
            if isinstance(cc_address, list):
                cc_address = ','.join(cc_address)
            self.email['CC'] = cc_address
        bcc_address = kwargs.get('bcc', False)
        if bcc_address:
            if isinstance(bcc_address, list):
                bcc_address = ','.join(bcc_address)
            self.email['BCC'] = bcc_address
        body_text = kwargs.get('body_text', False)
        body_html = kwargs.get('body_html', False)
        if body_text or body_html:
            self.add_body_text(body_text, body_html)

    @staticmethod
    def parse(raw_message):
        mail = Email()
        mail.email = email.message_from_string(raw_message)
        return mail

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

    def add_body_text(self, body_plain=False, body_html=False):
        """
        Add the Body Text to Email.
        Rises AttributeError if email already has a body text.
        Rises ValueError if no body_plain or body_html provided.
        :param body_plain:  Plain Text for the Body
        :type body_plain:   str
        :param body_html:   HTML Text for the Body
        :type body_html:    str
        :return:            True if updated, Raises an exception if failed. 
        :rtype:             bool
        """
        body_keys = self.body_parts.keys()
        if ('plain' in body_keys) or ('html' in body_keys):
            raise AttributeError('This email already has a body!')
            # TODO: create a new "local" email to replace the SELF with new body
        if not (body_html or body_plain):
            raise ValueError('No HTML or TEXT provided')
        body_plain = body_plain or html2text(body_html)
        body_html = body_html or body_plain
        msg_plain = MIMEText(body_plain, _subtype='plain')
        msg_html = MIMEText(body_html, _subtype='html')
        msg_part = MIMEMultipart(_subtype='alternative')
        msg_part.attach(msg_plain)
        msg_part.attach(msg_html)
        self.email.attach(msg_part)
        return True

    def add_attachment(self, fileobj):
        """
        Add an attachment file to the email
        :param filepath: Path to the file to attach
        :type filepath:  str
        :return:         True if Added, False if failed
        :rtype:          bool
        """
        if not fileobj:
            raise ValueError('File Obj not provided!')
        from os.path import basename
        import base64
        attachment = MIMEApplication('octet-stream')
        attachment.add_header(
            'Content-Disposition',
            'attachment; filename="%s"' % basename(fileobj.name)
        )
        attachment_str = base64.encodebytes(fileobj.read().encode('utf-8'))
        attachment.set_charset('utf-8')
        attachment.add_header('Content-Transfer-Encoding', 'base64')
        attachment.set_payload(
            attachment_str,
            charset=attachment.get_charset()
        )
        self.email.attach(attachment)
        return True

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

        :return: `address.Address`
        """
        return address.parse(self.header('From', ''))

    @property
    def to(self):
        """

        :return: `address.AddressList`
        """
        return address.parse_list(self.header('To', ''))

    @property
    def cc(self):
        """
        :return: `address.AddressList`
        """
        return address.parse_list(self.header('Cc', ''))

    @property
    def bcc(self):
        """
        :return: `address.AddressList`
        """
        return address.parse_list(self.header('Bcc', ''))

    @property
    def recipients(self):
        return self.to + self.cc + self.bcc

    @property
    def body_parts(self):
        """
        Get all body parts of the email (text, html and attachments)
        """
        return_vals = {}
        for part in self.email.walk():
            maintype, subtype = part.get_content_type().split('/')
            # Multipart/* are containers, so we skip it
            if maintype == 'multipart':
                continue
            # Get Text and HTML
            if maintype == 'text':
                if subtype in ['plain', 'html']:
                    return_vals.update(
                        {subtype:part.get_payload(decode=True).decode('utf-8')})
            # Get Attachments
            if maintype == 'application':
                files = return_vals.get('files', [])
                new_attach = part.get('Content-Disposition', False)
                if 'attachment' in new_attach:
                    filename = new_attach.split('filename=')[-1][1:-1]
                    if filename:
                        files.append(filename)
                return_vals['files'] = files
        return return_vals

    @property
    def attachments(self):
        """
        Get all attachments of the email.
        Return a Tuple as (AttachName, AttachContent) where the content is a
        base64 based string
        :return: Returns a Tuple generator as (AttachName, AttachContent)
        """
        for part in self.email.walk():
            if part.get_content_maintype() == 'application':
                new_attach = part.get('Content-Disposition', False)
                if 'attachment' in new_attach:
                    filename = new_attach.split('filename=')[-1][1:-1]
                    if filename:
                        yield filename, part.get_payload()

    @property
    def mime_string(self):
        return self.email.as_string()
