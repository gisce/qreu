from __future__ import absolute_import

from collections import namedtuple
try:
    from collections import UserList
except ImportError:
    from UserList import UserList
from email.utils import getaddresses, parseaddr


BaseAddress = namedtuple('Address', ['display_name', 'address'])

class Address(BaseAddress):
    @property
    def display(self):
        if self.display_name:
            return '{display_name} <{address}>'.format(**self._asdict())
        return self.address

    @staticmethod
    def parse(header):
        return parse(header)


def parse(header):
    """Parse email string using `parseaddr`
    :return: `Address` from parsing the address on `header`
    """
    return Address(*parseaddr(header))


def parse_list(header):
    """Parse a emails string using getaddresses.
    :return: `AddressList` from `header`
    """
    if not header:
        return AddressList([])
    else:
        return AddressList([header])


class AddressList(UserList):
    """Simple list to encapsulate emails.
    """
    @property
    def addresses(self):
      return [x[1] for x in getaddresses(self.data) if x[1]]
