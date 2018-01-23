# coding=utf-8
from __future__ import absolute_import, unicode_literals

import email
from email.header import decode_header, Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from html2text import html2text
from six import PY2

import re

from qreu import address
from qreu.sendcontext import get_current_sender


RE_PATTERNS = re.compile('({0})'.format('|'.join(
    [
        '^SV:',
        '^Antw:',
        '^VS:',
        '^RE:',
        '^AW:',
        '^Vá:',
        '^R:'
        '^RIF:',
        '^SV:',
        '^BLS:',
        '^Odp:',
        '^YNT:'
    ])), re.IGNORECASE)


FW_PATTERNS = re.compile('({0})'.format('|'.join(
    [
        '^VS:',
        '^Doorst:',
        '^VL:',
        '^TR:',
        '^WG:',
        '^Továbbítás:',
        '^I:',
        '^FS:',
        '^VB:',
        '^RV:',
        '^ENC:',
        '^PD:',
        '^İLT'
    ])), re.IGNORECASE)


class Email(object):
    """
    Correu object

    :param raw_message: Raw string message
    """
    def __init__(self, **kwargs):
        self.email = MIMEMultipart()
        for header_name in ['subject', 'from', 'to', 'cc', 'bcc']:
            value = kwargs.get(header_name, False)
            if not value:
                continue
            self.add_header(header_name, value)
        body_text = kwargs.get('body_text', False)
        body_html = kwargs.get('body_html', False)
        if body_text or body_html:
            self.add_body_text(body_text, body_html)

    @staticmethod
    def parse(raw_message):
        mail = Email()
        mail.email = email.message_from_string(raw_message)
        return mail

    def send(self):
        """
        Send himself using the current sendercontext
        """
        return get_current_sender().sendmail(self)

    @staticmethod
    def fix_header_name(header_name):
        """
        Fix header names according to RFC 4021:
        https://tools.ietf.org/html/rfc4021#section-2.1.5
        :param header_name: Name of the header to fix
        :type header_name:  str
        :return:            Fixed name of the header
        :rtype:             str
        """
        headers = [
            'Date', 'From', 'Sender', 'Reply-To', 'To', 'Cc', 'Bcc',
            'Message-ID', 'In-Reply-To', 'References', 'Subject', 'Comments',
            'Keywords', 'Resent-Date', 'Resent-From', 'Resent-Sender',
            'Resent-To', 'Resent-Cc', 'Resent-Bcc', 'Resent-Reply-To',
            'Resent-Message-ID', 'Return-Path', 'Received', 'Encrypted',
            'Disposition-Notification-To', 'Disposition-Notification-Options',
            'Accept-Language', 'Original-Message-ID', 'PICS-Label', 'Encoding',
            'List-Archive', 'List-Help', 'List-ID', 'List-Owner', 'List-Post',
            'List-Subscribe', 'List-Unsubscribe', 'Message-Context',
            'DL-Expansion-History', 'Alternate-Recipient',
            'Original-Encoded-Information-Types', 'Content-Return',
            'Generate-Delivery-Report', 'Prevent-NonDelivery-Report',
            'Obsoletes', 'Supersedes', 'Content-Identifier', 'Delivery-Date',
            'Expiry-Date', 'Expires', 'Reply-By', 'Importance',
            'Incomplete-Copy', 'Priority', 'Sensitivity', 'Language',
            'Conversion', 'Conversion-With-Loss', 'Message-Type',
            'Autosubmitted', 'Autoforwarded', 'Discarded-X400-IPMS-Extensions',
            'Discarded-X400-MTS-Extensions', 'Disclose-Recipients',
            'Deferred-Delivery', 'Latest-Delivery-Time',
            'Originator-Return-Address', 'X400-Content-Identifier',
            'X400-Content-Return', 'X400-Content-Type', 'X400-MTS-Identifier',
            'X400-Originator', 'X400-Received', 'X400-Recipients', 'X400-Trace',
            'MIME-Version', 'Content-ID', 'Content-Description',
            'Content-Transfer-Encoding', 'Content-Type', 'Content-Base',
            'Content-Location', 'Content-features', 'Content-Disposition',
            'Content-Language', 'Content-Alternative', 'Content-MD5',
            'Content-Duration',
        ]
        for header in headers:
            if header_name.lower() == header.lower():
                return header
        return ''

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
                elif isinstance(part[0], bytes):
                    result.append(part[0].decode('utf-8'))
                else:
                    result.append(part[0])
            header_value = ''.join(result)

        return header_value

    def add_header(self, header, value):
        """
        Add (or replace) the header `key` with the UTF-8 encoded `value`
        Also parses lists if a recipient header (to, cc or bcc)
        :param header:  Key of the MIME Message Header
        :type header:   str
        :param value:   Value of the MIME Message Header
        :type value:    str, list
        :return:        New Header Value
        :raises:        ValueError
        """
        if not (header and value):
            raise ValueError('Header not provided!')
        recipients_headers = ['to', 'cc', 'bcc']
        if header.lower() in recipients_headers or header.lower() == 'from':
            if not isinstance(value, list):
                value = [value]
            header_value = []
            for addr in value:
                # For each address in the recipients headers
                # Do the Header Object
                # PY3 works fine with Header(values, charset='utf-8')
                # PY2:
                # - Does not escape correctly the unicode values
                # - Must encode the display name as a HEADER
                #    so the item is encoded properly
                # - The encoded display name and the address are joined
                #    into the Header of the email
                mail_addr = address.parse(addr)
                display_name = Header(
                    mail_addr.display_name, charset='utf-8').encode()
                if display_name:
                    # decode_header method in PY2 does not look for closed items
                    # so a ' ' separator is required between items of a Header
                    if PY2:
                        base_addr = '{} <{}>'
                    else:
                        base_addr = '{}<{}>'
                    header_value.append(
                        base_addr.format(
                            display_name,
                            mail_addr.address
                        ).strip()
                    )
                else:
                    header_value.append(mail_addr.address)
            header_value = ','.join(header_value)
        else:
            header_value = Header(value, charset='utf-8').encode()
        # Get correct header name or add the one provided if custom header key
        header = Email.fix_header_name(header) or header
        self.email[header] = header_value
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
        if body_plain and ('plain' in body_keys):
            raise AttributeError('This email already has a plain body!')
        if body_html and ('html' in body_keys):
            raise AttributeError('This email already has an HTML body!')
            # TODO: create a new "local" email to replace the SELF with new body
        if not (body_html or body_plain):
            raise ValueError('No HTML or TEXT provided')
        body_plain = body_plain or html2text(body_html)
        msg_plain = MIMEText(body_plain, _subtype='plain', _charset='utf-8')
        msg_part = MIMEMultipart(_subtype='alternative')
        msg_part.attach(msg_plain)
        if body_html:
            msg_html = MIMEText(body_html, _subtype='html', _charset='utf-8')
            msg_part.attach(msg_html)
        self.email.attach(msg_part)
        return True

    def add_attachment(self, input_buff=False, input_b64=False, attname=False):
        """
        Add an attachment file to the email
        :param input_buff:  Buffer of the file to attach (something to read)
        :type input_buff:   Buffer
        :param input_b64:  Base64-based string to attach as file
        :type input_b64:   str or bytes
        :param attname:    Name of the attachment
        :type attname:     str
        :return:           True if Added, Exception if failed
        :rtype:            bool
        """
        if not (input_buff or input_b64):
            raise ValueError('Attachment not provided!')
        try:
            # Try to get name from input if not provided
            filename = attname or input_buff.name
        except AttributeError:
            raise ValueError('Name of the attachment not provided')
        from os.path import basename
        import base64
        attachment = MIMEApplication('octet-stream')

        attachment.add_header(
            'Content-Disposition',
            'attachment; filename="%s"' % basename(filename)
        )
        if input_buff:
            attachment_str = base64.encodestring(
                input_buff.read().encode('utf-8'))
        elif input_b64:
            attachment_str = input_b64

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
