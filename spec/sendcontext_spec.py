# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from qreu import sendcontext
from qreu import Email

from mamba import *
from expects import *

with description('Simple SenderManager'):
    with context('simple configuration'):
        with before.all:
            def send_true(mail):
                return True
            self.manager = sendcontext.SenderContext()
            self.send_true = send_true
            self.test_mail = Email()
        with it('must create a new simple configuration'):
            expect(self.manager.has_configs()).to(be_false)
            self.manager.add_config(send_method=self.send_true)
            expect(self.manager.has_configs()).to(be_true)

        with it('must "send" correctly any email from config'):
            for config in self.manager.configs:
                expect(config.send(self.test_mail)).to(be_true)
