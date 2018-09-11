# coding=utf-8
from __future__ import absolute_import, unicode_literals
from qreu import Email
from qreu.address import AddressList, Address
from qreu.sendcontext import Sender
from datetime import datetime, tzinfo, timedelta
from mock import patch
import qreu.address

from email.utils import formatdate
from email.mime.multipart import MIMEMultipart
from html2text import html2text

from mamba import *
from expects import *

from six import PY2

with description('Parsing an Email'):
    with before.all:
        self.raw_messages = []
        for fixture in range(0, 5):
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

    with it('must only remove FW and RV patterns'):
        c = Email.parse("Subject: =?utf-8?q?Recordatori=3A_?=")
        expect(c.subject).to(equal("Recordatori:"))

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

    with it('must get all attachments and avoid wrong body parts'):
        c = Email.parse(self.raw_messages[4])
        attch = [p for p in c.attachments]
        expect(attch).to(be_empty)
        expect(c.body_parts['files']).to(be_empty)

with description("Creating an Email"):
    with context("empty"):
        with it("must have all attributes to None and work"):
            e = Email()
            expect(e.subject).to(be_empty)
            expect(e.to).to(be_empty)
            expect(e.cc).to(be_empty)
            expect(e.recipients).to(be_empty)
            expect(e.recipients.addresses).to(be_empty)
            expect(e.bcc).to(be_empty)
            expect(e.bccs).to(be_empty)

        with it('must add date to Header on create'):
            d = datetime.now()
            e = Email()
            if PY2:
                t = (d - datetime(1970, 1, 1)).total_seconds()
            else:
                t = d.timestamp()
            # IF Py3 use "d.timestamp()"
            expect(e.header('Date')).to(equal(
                formatdate(t) 
            ))

        with it('must add date to Header on create providing a String'):
            d = datetime.now()
            if PY2:
                t = (d - datetime(1970, 1, 1)).total_seconds()
            else:
                t = d.timestamp()
            s = formatdate(t)
            e = Email(date=s)
            expect(e.header('Date')).to(equal(s))

        with it('must add date to Header on create providing a Datetime'):
            d = datetime.now()
            if PY2:
                t = (d - datetime(1970, 1, 1)).total_seconds()
            else:
                t = d.timestamp()
            e = Email(date=d)
            expect(e.header('Date')).to(equal(
                formatdate(t)
            ))

        with it('must add date to Header on create providing a'
                ' TZ Aware Datetime'):
            class timezone(tzinfo):

                def tzname(self, dt):
                    return str('Custom')

                def utcoffset(self, dt):
                    diff = (
                        timedelta(hours=dt.hour, minutes=dt.minute) + 
                        timedelta(hours=1, minutes=23)
                    )
                    return diff

                def dst(self, dt):
                    return self.utcoffset(dt)

            info = timezone()
            d = datetime.now(tz=info)
            if PY2:
                utc_naive = (d.replace(tzinfo=None) - d.utcoffset())
                t = (utc_naive - datetime(1970, 1, 1)).total_seconds()
            else:
                t = d.timestamp()
            e = Email(date=d)
            expect(e.header('Date')).to(equal(
                formatdate(t)
            ))

        with it('must add any header to Email'):
            e = Email()
            header_key = 'X-ORIG-HEADER'
            header_value = 'Header String Value'
            expect(e.header(header_key, False)).to(be_false)
            # Custom Header
            e.add_header(header_key, header_value)
            # Recipient Header using an address
            e.add_header('to', 'someone@example.com')
            # Recipient Header using a list
            e.add_header('cc', ['someone@example.com', 'theboss@example.com'])
            expect(e.header(header_key, False)).to(equal(header_value))

        with it("must NOT add BCC Header, but ADD 'bccs' attribute"):
            e = Email()
            bccs = [
                'secret@example.com',
                'email2@example.com'
            ]
            expect(e.add_header('bcc', bccs)).to(equal(','.join(bccs)))
            expect(e.header('bcc', [])).to(be_empty)
            expect(e.bccs).to(equal(','.join(bccs)))

        with it('must raise exception wrongly adding a header'):
            def call_wrongly():
                e = Email()
                header_key = 'X-ORIG-HEADER'
                expect(e.header(header_key, False)).to(be_false)
                e.add_header(header_key, False)
            expect(call_wrongly).to(raise_error(ValueError))

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
            expect(e.body_parts).to(have_key('plain'))
            expect(e.body_parts).to_not(have_key('html'))
            expect(e.body_parts['plain']).to(equal(plain))

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

        with it('must be able to add plain and html to the body separately'):
            e = Email()
            html = 'Html-based body for the e-mail'
            plain = html2text(html)
            e.add_body_text(body_plain=plain)
            e.add_body_text(body_html=html)
            expect(e.body_parts).to(have_keys('plain', 'html'))
            expect(e.body_parts['plain']).to(equal(plain))
            expect(e.body_parts['html']).to(equal(html))

        with it('must raise AtributeErrpr if adding the body a 2nd time'):
            def call_wrongly_plain():
                e = Email()
                e.add_body_text(body_plain='some_body_text')
                e.add_body_text(body_plain='some_body_text')
            def call_wrongly_html():
                e = Email()
                e.add_body_text(body_html='some_body_text')
                e.add_body_text(body_html='some_body_text')
            expect(call_wrongly_plain).to(raise_error(AttributeError))
            expect(call_wrongly_html).to(raise_error(AttributeError))

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
            files = [attachment['name'] for attachment in e.attachments]
            expect(files).to(equal([f_name, f_name]))
            for attachment in e.attachments:
                filename = attachment['name']
                filecontent = attachment['content']
                with open(f_path) as f:
                    attachment_str = base64.encodestring(
                        f.read().encode('utf-8'))
                    try:
                        attachment_str = str(attachment_str, 'utf-8')
                    except TypeError:
                        # Python 2.7 compat
                        attachment_str = unicode(attachment_str)
                expect(filecontent).to(equal(attachment_str))

        with it('must add an iostring as attachment to body'):
            import base64
            from io import StringIO
            e = Email()
            f_path = 'spec/fixtures/0.txt'
            f_name = '0.txt'
            with open(f_path, 'r') as f:
                f_data = f.read()
            try:
                input_iostr = StringIO(f_data)
            except TypeError:
                # Python 2.7 compat
                input_iostr = StringIO(unicode(f_data))
            check_str = base64.encodestring(f_data.encode('utf-8'))
            try:
                check_str = str(check_str, 'utf-8')
            except TypeError:
                # Python 2.7 compat
                check_str = unicode(check_str)
            e.add_attachment(input_buff=input_iostr, attname=f_name)
            for attachment in e.attachments:
                filename = attachment['name']
                filecontent = attachment['content']
                expect(filecontent).to(equal(check_str))

        with it('must add a base64 string as attachment to body'):
            import base64
            from io import StringIO
            e = Email()
            f_path = 'spec/fixtures/0.txt'
            f_name = '0.txt'
            with open(f_path) as f:
                f_data = f.read()
            base64_str = base64.encodestring(f_data.encode('utf-8'))
            try:
                base64_str = str(base64_str, 'utf-8')
            except TypeError:
                # Python 2.7 compat
                base64_str = unicode(base64_str)
            e.add_attachment(input_b64=base64_str, attname=f_name)
            for attachment in e.attachments:
                filename = attachment['name']
                filecontent = attachment['content']
                expect(filecontent).to(equal(base64_str))

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
        with it("must not add BCC header, but ADD 'bccs' attribute"):
            bccs = self.vals['bcc']
            e = Email(**{'bcc': self.vals['bcc']})
            expect(e.header('bcc', [])).to(be_empty)
            expect(e.bccs).to(equal(','.join(bccs)))
            expect(e.bcc).to(equal([','.join(bccs)]))
        
        with it("must have all headers and text(basic MIMEMultipart)"):
            e = Email(**self.vals)
            expect(e.subject).to(equal(self.vals['subject']))
            expect(e.to).to(equal(self.vals['to']))
            expect(e.from_).to(equal(qreu.address.parse(self.vals['from'])))
            expect(e.cc).to(equal([','.join(self.vals['cc'])]))
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

        with it('must add addresses correctly as "name" <address>'):
            address = 'spécial <special@example.com>'
            parsed = 'spécial<special@example.com>'
            e = Email(to=address)
            expect(e.to).to(equal([parsed]))
            e = Email(cc=address)
            expect(e.cc).to(equal([parsed]))
            e = Email(bcc=[address])
            expect(e.bcc).to(equal([parsed]))

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

        with it('must send himself using current sendcontext'):
            e = Email(**self.vals)
            with Sender():
                expect(e.send()).to(equal(e.mime_string))
        
        with it('must not re-add "Date" on email when adding header'):
            e = Email(**self.vals)
            expect(e.header('Date')).to_not(be_false)
            expect(e.add_header('Date', e.header('Date'))).to(be_false)
            expect(len(e.mime_string.split('Date'))).to(equal(2))
