# -*- coding: utf-8 -*-

from qreu import local
from qreu.address import Address
from smtplib import SMTP, SMTP_SSL, SMTPConnectError

_SENDCONTEXT = local.LocalStack()

def get_current_sender():
    return _SENDCONTEXT.top

class Sender(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            self.__setattr__(k, v)

    def __enter__(self):
        _SENDCONTEXT.push(self)
        return _SENDCONTEXT.top

    def __exit__(self, etype, evalue, etraceback):
        _SENDCONTEXT.pop()

    def sendmail(self, mail):
        """
        Send the qreu.Email object as a string
        :param mail:    qreu.Email object to send
        :type mail:     Email
        """
        return mail.mime_string

    def send(self, mail):
        """
        Catch the current sender from the context and send the email with it
        :param mail:    qreu.Email object to send
        :type mail:     Email
        """
        sender = get_current_sender()
        return sender.sendmail(mail)


class FileSender(Sender):
    def __init__(self, filename):
        if not filename:
            raise ValueError('A filename is required to spawn a FileSender')
        super(FileSender, self).__init__(_filename=filename)

    def sendmail(self, mail):
        """
        Send the qreu.Email object as a string to a file
        :param mail:    qreu.Email object to send
        :type mail:     Email
        """
        with open(self._filename, 'w') as writer:
            writer.write(mail.mime_string)
        return True

class SMTPSender(Sender):
    def __init__(
            self, host='localhost', port=25, user=None, passwd=None,
            ssl_keyfile=None, ssl_certfile=None, tls=False, ssl=False
    ):
        """
        Sender context to send through SMTP
        :param host:            Host to the SMTP Server
        :type host:             str
        :param port:            Port for the SMTP Connection (Default is 25)
        :type port:             int
        :param user:            User for the SMTP Connection Login
        :type user:             str
        :param passwd:          Password for the SMTP Connection Login
        :type passwd:           str
        :param ssl_keyfile:     Path to the SSL keyfile (TLS Connection)
        :type ssl_keyfile:      str
        :param ssl_certfile:    Path to the SSL certfile (TLS Connection)
        :type ssl_certfile:     str
        :param tls:             Start TLS after basic SMTP connection
        :type tls:              boolean
        :param ssl:             Start connection as SMTP-SSL
        :type ssl:              boolean
        """
        super(SMTPSender, self).__init__(
            _host=host, _port=port,
            _user=user, _passwd=passwd,
            _ssl_keyfile=ssl_keyfile, _ssl_certfile=ssl_certfile,
            _tls=tls or (ssl_certfile and ssl_keyfile),
            _ssl=ssl
        )

    def __enter__(self):
        if self._ssl:
            self._connection = SMTP_SSL(
                host=self._host, port=self._port,
                keyfile=self._ssl_keyfile, certfile=self._ssl_certfile
            )
        else:
            try:
                self._connection = SMTP(host=self._host, port=self._port)
                if self._tls:
                    self._connection.starttls(
                        keyfile=self._ssl_keyfile, certfile=self._ssl_certfile)
            except SMTPConnectError as err:
                # Cannot establish connection due to only listening to SSL
                if self._tls or self._ssl:
                    self._connection = SMTP_SSL(
                        host=self._host, port=self._port,
                        keyfile=self._ssl_keyfile, certfile=self._ssl_certfile
                    )
                else:
                    raise
        if self._user and self._passwd:
            self._connection.login(user=self._user, password=self._passwd)
        return super(SMTPSender, self).__enter__()

    def __exit__(self, etype, evalue, etraceback):
        super(SMTPSender, self).__exit__(etype, evalue, etraceback)
        self._connection.close()

    def sendmail(self, mail):
        """
        Send the qreu.Email object through smtp.sendmail
        :param mail:    qreu.Email object to send
        :type mail:     Email
        """
        from_mail = mail.from_
        if isinstance(mail.from_, Address):
            from_mail = from_mail.address
        self._connection.sendmail(
            from_mail, mail.recipients_addresses, mail.mime_string)
        return True
