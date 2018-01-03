# coding=utf-8
from __future__ import absolute_import, unicode_literals
from qreu import Email
from qreu.address import AddressList, Address
import qreu.address

from email.mime.multipart import MIMEMultipart
from html2text import html2text

from mamba import *
from expects import *


with description('Parsing an Email'):
    with before.all:
        self.raw_messages = []
        for fixture in range(0, 4):
            with open('spec/fixtures/{0}.txt'.format(fixture)) as f:
                self.raw_messages.append(f.read())

    with it('must be initialized with a raw message'):
        c = Email.parse(self.raw_messages[0])

    with it('must know if is a reply or not'):
        c = Email.parse(self.raw_messages[0])
        expect(c.is_reply).to(be_false)

    with it('must clean subjects from Replies'):
        c = Email.parse(self.raw_messages[1])
        expect(c.email.get('Subject')).to(equal('Re: [gisce/tipoinstalacion] Add spec for ct (#5)'))
        expect(c.subject).to(equal('[gisce/tipoinstalacion] Add spec for ct (#5)'))

    with it('must kwnon if a email is fowared'):
        c = Email.parse(self.raw_messages[2])
        expect(c.is_forwarded).to(be_true)

    with it('must known all the references'):
        c = Email.parse(self.raw_messages[3])
        expect(c.references).to(contain_exactly(
            '<001f01d1d29d$69440960$3bcc1c20$@client.example.com>',
            '<CA+y8Mvn42Yn2B4GOaZOMQ3TwNLwC7u24FBp26moih2RFjzUeEA@mail.mailservice.example.com>',
            '<CA+y8Mv=H0YsjToZJ36fhNYT=0X5g2LapQzUidH-+Q-MkMP_15Q@mail.mailservice.example.com>',
            '<CA+y8Mvk4ThFSS_1tQGS9UsfL8T8grEc2WSQSb5rsdFBTspP9NQ@mail.mailservice.example.com>',
            '<003901d1d2d0$5fde26c0$1f9a7440$@client.example.com>'
        ))

    with it('must know his parent'):
        c = Email.parse(self.raw_messages[3])
        expect(c.parent).to(equal('<003901d1d2d0$5fde26c0$1f9a7440$@client.example.com>'))

        with context('And if it does not have parent'):
            with it('must return None'):
                c = Email.parse(self.raw_messages[0])
                expect(c.parent).to(be_none)

    with context('with an empty string'):
        with it('must work'):
            c = Email.parse('')
        with it('must evaluate to False'):
            c = Email.parse('')
            expect(bool(c)).to(be_false)

    with it('must return objects for From, To, Cc and Bcc'):
        c = Email.parse(self.raw_messages[0])
        expect(c.from_.address).to(equal('notifications@git.example.com'))
        expect(c.from_.display_name).to(equal('User'))

        expect(c.to).to(be_a(AddressList))
        expect(c.to.addresses).to(contain_exactly(
            'qreu@noreply.git.example.com',
            'other@example.com'
        ))

        expect(c.cc.addresses).to(contain_exactly(
            'thebest@example.com'
        ))

        expect(c.bcc.addresses).to(contain_exactly(
            'theboss@example.com'
        ))

    with it('must have a recipients properties'):
        c = Email.parse(self.raw_messages[0])

        expect(c.recipients.addresses).to(contain_exactly(
            'qreu@noreply.git.example.com',
            'other@example.com',
            'thebest@example.com',
            'theboss@example.com'
        ))

    with it('must to decode headers'):
        c = Email.parse("Subject: =?iso-8859-1?Q?ERROR_A_L'OBRIR_EL_LOT_DE_PERFILACI=D3_JUNY?=")
        expect(c.subject).to(equal(u"ERROR A L'OBRIR EL LOT DE PERFILACIÓ JUNY"))

with description("Creating an Email"):
    with context("empty"):
        with it("must have all attributes to None and work"):
            e = Email()
            expect(e.subject).to(be_empty)
            expect(e.to).to(be_empty)
            expect(e.cc).to(be_empty)
            expect(e.recipients).to(be_empty)

        with it('must add body to Email'):
            e = Email()
            plain = 'Text-based body for the e-mail'
            html = 'Html-based body for the e-mail'
            e.add_body_text(body_plain=plain, body_html=html)
            expect(e.body_parts).to(have_keys('plain', 'html'))
            expect(e.body_parts['plain']).to(equal(plain))
            expect(e.body_parts['html']).to(equal(html))

        with it("must add body to Email with only plain text"):
            e = Email()
            plain = 'Text-based body for the e-mail'
            e.add_body_text(body_plain=plain)
            expect(e.body_parts).to(have_keys('plain', 'html'))
            expect(e.body_parts['plain']).to(equal(plain))
            expect(e.body_parts['html']).to(equal(plain))

        with it("must add body to Email with only html text"):
            e = Email()
            html = 'Html-based body for the e-mail'
            plain = html2text(html)
            e.add_body_text(body_html=html)
            expect(e.body_parts).to(have_keys('plain', 'html'))
            expect(e.body_parts['plain']).to(equal(plain))
            expect(e.body_parts['html']).to(equal(html))
        
        with it('must raise ValueError if no body provided on add_body'):
            e = Email()
            expect(e.add_body_text).to(raise_error(ValueError))

        with it('must raise AtributeErrpr if adding the body a 2nd time'):
            e = Email()
            e.add_body_text('some_body_text')
            expect(e.add_body_text).to(raise_error(AttributeError))

        with it('must add an attachments to body'):
            import base64
            e = Email()
            f_path = 'spec/fixtures/0.txt'
            f_name = '0.txt'
            with open(f_path) as f:
                expect(e.add_attachment(input_buff=f)).to(be_true)
            expect(e.body_parts).to(have_key('files'))
            expect(e.body_parts['files']).to(equal([f_name]))
            with open(f_path) as f:
                expect(e.add_attachment(input_buff=f)).to(be_true)
            files = [filename for filename, filecontent in e.attachments]
            expect(files).to(equal([f_name, f_name]))
            for filename, filecontent in e.attachments:
                with open(f_path) as f:
                    attachment_str = str(base64.encodebytes(
                        f.read().encode('utf-8')), 'utf-8')
                expect(filecontent).to(equal(attachment_str))
        
        with it('must add an iostring as attachment to body'):
            import base64
            from io import StringIO
            e = Email()
            f_path = 'spec/fixtures/0.txt'
            f_name = '0.txt'
            with open(f_path) as f:
                f_data = f.read()
            input_iostr = StringIO(f_data)
            check_str = str(
                base64.encodebytes(f_data.encode('utf-8')), 'utf-8')
            e.add_attachment(input_buff=input_iostr, attname=f_name)
            for filename, filecontent in e.attachments:
                expect(filecontent).to(equal(check_str))

        with it('must raise an exception adding an unexisting attachment'):
            def call_wrongly():
                e = Email()
                e.add_attachment(False)
            
            expect(call_wrongly).to(raise_error(ValueError))

        with it('must raise an exception adding an attachment without name'):
            import base64
            from io import StringIO
            def call_wrongly():
                e = Email()
                input_iostr = StringIO('Test string on StringIO')
                e.add_attachment(input_iostr)
            
            expect(call_wrongly).to(raise_error(ValueError))

    with context("using kwargs"):
        with before.all:
            self.vals = {
                'subject': 'Test message',
                'to': ['to@example.com'],
                'from': 'from@example.com',
                'cc': [
                    'another@example.com',
                    'email@example.com'
                ],
                'bcc': [
                    'secret@example.com',
                    'email2@example.com'
                ],
                'body_text': 'Text-based body for the e-mail',
                'body_html': (
                    "<div>Test email:</div>"
                    "<ul><li>This</li><li>Is</li><li>A</li><li>List</li></ul>"
                    "<div><b>IMPORTANT sentence</b><br/>"
                    "<i>italic sentence</i><br/>"
                    "And <u>underline</u></div>"
                )
            }
        with it("must have all headers and text(basic MIMEMultipart)"):
            e = Email(**self.vals)
            expect(e.subject).to(equal(self.vals['subject']))
            expect(e.to).to(equal(self.vals['to']))
            expect(e.from_).to(equal(qreu.address.parse(self.vals['from'])))
            expect(e.cc).to(equal([','.join(self.vals['cc'])]))
            expect(e.bcc).to(equal([','.join(self.vals['bcc'])]))
            recipients = list({
                ','.join(self.vals['to']),
                ','.join(self.vals['cc']),
                ','.join(self.vals['bcc'])
            })
            failed_vals = []
            for elem in recipients:
                if elem not in e.recipients:
                    failed_vals.append(elem)
            expect(failed_vals).to(be_empty)
            failed_vals = []
            for elem in e.recipients:
                if elem not in recipients:
                    failed_vals.append(elem)
            expect(failed_vals).to(be_empty)
            expect(e.body_parts).to(have_keys('plain', 'html'))
            expect(e.body_parts['plain']).to(equal(self.vals['body_text']))
            expect(e.body_parts['html']).to(equal(self.vals['body_html']))

        with it('must parse text2html if no html provided'):
            vals = self.vals.copy()
            vals.pop('body_html')
            e = Email(**vals)
            expect(e.body_parts).to(have_keys('plain', 'html'))
            expect(e.body_parts['html']).to(equal(vals['body_text']))

        with it('must parse html2text if no text provided'):
            vals = self.vals.copy()
            vals.pop('body_text')
            body_text = html2text(vals['body_html'])
            e = Email(**vals)
            expect(e.body_parts).to(have_keys('plain', 'html'))
            expect(e.body_parts['plain']).to(equal(body_text))
        
        with it('must return the email as MIME-formated string'):
            e = Email(**self.vals)
            expect(
                Email.parse(e.mime_string).mime_string
            ).to(equal(e.mime_string))
