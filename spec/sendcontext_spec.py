# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from mamba import *
from expects import *
from mock import patch, Mock
import shutil
import tempfile

from qreu.sendcontext import *
from qreu import Email
from smtplib import SMTPConnectError

with description('Senders'):
    with before.all:
        class TempDir(object):
            def __init__(self):
                self.dir = tempfile.mkdtemp()

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                shutil.rmtree(self.dir)
        self.temp_dir = TempDir
        self.test_mail = Email(
            From='me@example.com',
            To='you@example.com',
            Subject='test_email',
            body_text='''
            This is a test email.
            If you recieved this email, it means we sent it correctly.
            '''
        )

    with it('must send different emails on multi-layered contexts'):
        with self.temp_dir() as tmpdir:
            filename = tempfile.mktemp(dir=tmpdir.dir)
            with Sender() as base_sender:
                expect(base_sender.send(self.test_mail)).to(
                    equal(self.test_mail.mime_string))
                with FileSender(filename) as file_sender:
                    file_sender.send(self.test_mail)
                with open(filename, 'r') as file_mail:
                    expect(file_mail.read()).to(
                        equal(self.test_mail.mime_string))
                expect(base_sender.send(self.test_mail)).to(
                    equal(self.test_mail.mime_string))

    with context('Bad Sender inits'):
        with it('must raise ValueError if no filename provided to FileSender'):
            def call_wrongly():
                FileSender(False)

            expect(call_wrongly).to(raise_error(ValueError))

    with context('Default (DEBUG) Sender'):
        with it('must return the mail as a string with default Sender'):
            with Sender() as sender:
                expect(sender.send(self.test_mail)).to(
                    equal(self.test_mail.mime_string))

    with context('FILE Sender'):
        with it('must write the mail as a string to a file with FileSender'):
            with self.temp_dir() as tmpdir:
                filename = tempfile.mktemp(dir=tmpdir.dir)
                with FileSender(filename) as sender:
                    sender.send(self.test_mail)
                with open(filename, 'r') as test_file:
                    mail_text = test_file.read()
                expect(mail_text).to(equal(self.test_mail.mime_string))

    with context('SMTP Sender'):
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

        with it('must try SMTP_SSL connection after failure if TLS is enabled'):
            with patch('qreu.sendcontext.SMTP') as msmtp:
                msmtp.side_effect = SMTPConnectError(
                    530, "5.7.0 Must issue a STARTTLS command first.")
                with patch('qreu.sendcontext.SMTP_SSL') as msmtp_ssl:
                    smtp_mocked = Mock()
                    smtp_mocked.login.return_value = True
                    smtp_mocked.starttls.return_value = True
                    smtp_mocked.login.return_value = True
                    smtp_mocked.send.return_value = True
                    smtp_mocked.sendmail.return_value = True
                    smtp_mocked.close.return_value = True
                    msmtp_ssl.return_value = smtp_mocked
                    with SMTPSender(
                            host='host',
                            user='user',
                            passwd='passwd',
                            ssl_keyfile='ssl_keyfile',
                            ssl_certfile='ssl_certfile'
                    ) as sender:
                        expect(sender.send(self.test_mail)).to(be_true)

        with it('must raise exception after Failure if no TLS is enabled'):
            def call_wrongly():
                with SMTPSender(
                        host='host',
                        user='user',
                        passwd='passwd',
                        ssl_keyfile=False,
                        ssl_certfile=False
                ) as sender:
                    expect(sender.send(self.test_mail)).to(be_true)
            with patch('qreu.sendcontext.SMTP') as msmtp:
                msmtp.side_effect = SMTPConnectError(
                    530, "5.7.0 Must issue a STARTTLS command first.")
                expect(call_wrongly).to(raise_error)
