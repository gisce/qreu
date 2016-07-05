# coding=utf-8
from __future__ import absolute_import
from qreu import Email

from expects import *


with description('An Email'):
    with before.all:
        self.raw_messages = []
        for fixture in range(0, 4):
            with open('spec/fixtures/{0}.txt'.format(fixture)) as f:
                self.raw_messages.append(f.read())

    with it('must be initialized with a raw message'):
        c = Email(self.raw_messages[0])

    with it('must clean subjects from Replies'):
        c = Email(self.raw_messages[1])
        expect(c.email.get('Subject')).to(equal('Re: [gisce/tipoinstalacion] Add spec for ct (#5)'))
        expect(c.subject).to(equal('[gisce/tipoinstalacion] Add spec for ct (#5)'))

    with it('must kwnon if a email is fowared'):
        c = Email(self.raw_messages[2])
        expect(c.is_forwarded).to(be_true)

    with it('must known all the references'):
        c = Email(self.raw_messages[3])
        expect(c.references).to(contain_exactly(
            '<001f01d1d29d$69440960$3bcc1c20$@client.example.com>',
            '<CA+y8Mvn42Yn2B4GOaZOMQ3TwNLwC7u24FBp26moih2RFjzUeEA@mail.mailservice.example.com>',
            '<CA+y8Mv=H0YsjToZJ36fhNYT=0X5g2LapQzUidH-+Q-MkMP_15Q@mail.mailservice.example.com>',
            '<CA+y8Mvk4ThFSS_1tQGS9UsfL8T8grEc2WSQSb5rsdFBTspP9NQ@mail.mailservice.example.com>',
            '<003901d1d2d0$5fde26c0$1f9a7440$@client.example.com>'
        ))

    with it('must know his parent'):
        c = Email(self.raw_messages[3])
        expect(c.parent).to(equal('<003901d1d2d0$5fde26c0$1f9a7440$@client.example.com>'))

        with context('And if it does not have parent'):
            with it('must return None'):
                c = Email(self.raw_messages[0])
                expect(c.parent).to(be_none)

    with context('with an empty string'):
        with it('must work'):
            c = Email('')
        with it('must evaluate to False'):
            c = Email('')
            expect(bool(c)).to(be_false)
