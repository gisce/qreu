# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from qreu.sendcontext import *
from qreu import Email

from mamba import *
from expects import *

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

    with _it('must write the mail as a string to a file with FileSender'):
        filename = 'test_filesender'
        with FileSender(filename) as sender:
            sender.send(self.test_mail)
        with open(filename, 'r') as test_file:
            mail_text = test_file.read()
        expect(mail_text).to(equal(self.test_mail.mime_string))

    with _it('must "send" via smtp the email with SMTPSender'):
        # TODO: Mock it
        with SMTPSender(host='', user='', passwd='', ssl=True) as sender:
            sender.send(self.test_mail)
