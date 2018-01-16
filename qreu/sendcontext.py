# -*- coding: utf-8 -*-

from qreu import local

_SENDCONTEXT = local.LocalStack()

class Sender(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            self.__setattr__(k, v)

    def __enter__(self):
        _SENDCONTEXT.push(self)
        return _SENDCONTEXT.top

    def __exit__(self, a, b, c):
        _SENDCONTEXT.pop()

    def send(self, mail):
        """
        Send the qreu.Email object as a string
        :param mail:    qreu.Email object to send
        :type mail:     Email
        """
        return mail.mime_string


class FileSender(Sender):
    def __init__(self, filename):
        if not filename:
            raise ValueError('A filename is required to spawn a FileSender')
        super(FileSender, self).__init__(_filename=filename)

    def send(self, mail):
        """
        Send the qreu.Email object as a string to a file
        :param mail:    qreu.Email object to send
        :type mail:     Email
        """
        with open(self._filename, 'w') as writer:
            writer.write(mail.mime_string)