# -*- coding: utf-8 -*-

from qreu import local
from smtplib import SMTP

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
            self, host='localhost', port=0, user=None, passwd=None,
            ssl_keyfile=None, ssl_certfile=None, tls=False
    ):
        super(SMTPSender, self).__init__(
            _host=host,
            _port=port,
            _user=user,
            _passwd=passwd,
            _ssl_keyfile=ssl_keyfile,
            _ssl_certfile=ssl_certfile,
            _tls=tls or (ssl_certfile and ssl_keyfile)
        )

    def __enter__(self):
        self._connection = SMTP(host=self._host, port=self._port)
        if self._tls:
            self._connection.starttls(
                keyfile=self._ssl_keyfile, certfile=self._ssl_certfile)
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
        self._connection.sendmail(mail.from_, mail.recipients, mail.mime_string)
        return True
