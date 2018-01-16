# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from qreu import sendcontext
from qreu import Email

from mamba import *
from expects import *

with description('Sendcontext'):
    with before.all:
        self.test_mail = Email()
    with it('must return the mail as a string with default Sender'):
        with sendcontext.Sender() as sender:
            expect(sender.send(self.test_mail)).to(
                equal(self.test_mail.mime_string))
