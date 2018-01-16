# -*- coding: utf-8 -*-

from qreu import local

_SENDCONTEXT = local.LocalStack()

class Sender():
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
