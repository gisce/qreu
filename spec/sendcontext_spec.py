# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from qreu.sendcontext import *
from qreu import Email

from mamba import *
from expects import *

from mock import patch, Mock

with description('Sendcontext'):
    with before.all:
        self.test_mail = Email(
            From='me@example.com',
            To='you@example.com',
            Subject='test_email',
            body_text='''
            This is a test email.
            If you recieved this email, it means we sent it correctly.
            '''
        )
    with it('must return the mail as a string with default Sender'):
        with Sender() as sender:
            expect(sender.send(self.test_mail)).to(
                equal(self.test_mail.mime_string))

    with it('must write the mail as a string to a file with FileSender'):
        filename = 'test_filesender'
        with FileSender(filename) as sender:
            sender.send(self.test_mail)
        with open(filename, 'r') as test_file:
            mail_text = test_file.read()
        expect(mail_text).to(equal(self.test_mail.mime_string))

    with it('must "send" via smtp the email with SMTPSender'):
        with patch('qreu.sendcontext.SMTP') as mocked_conn:
            # Mock the SMTP connection
            smtp_mocked = Mock()
            smtp_mocked.login.return_value = True
            smtp_mocked.starttls.return_value = True
            smtp_mocked.login.return_value = True
            smtp_mocked.send.return_value = True
            smtp_mocked.sendmail.return_value = True
            smtp_mocked.close.return_value = True
            mocked_conn.return_value = smtp_mocked
            with SMTPSender(
                host='host',
                user='user',
                passwd='passwd',
                ssl_keyfile='ssl_keyfile',
                ssl_certfile='ssl_certfile'
            ) as sender:
                sender.send(self.test_mail)
