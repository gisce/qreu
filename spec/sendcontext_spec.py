# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from qreu import sendcontext

from mamba import *
from expects import *

with description('Simple SenderManager'):
    with it(
        'must create a new configuration, add it to SenderManager'
        ' and be able to send'
    ):
        def send_true():
            return True
        manager = sendcontext.SenderContext()
        manager.add_config(send_method=send_true)
        expect(manager.has_configs()).to(be_true)
        expect([c.send() for c in manager.configs]).to(equal([True]))
