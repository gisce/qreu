from __future__ import absolute_import

from collections import namedtuple
try:
    from collections import UserList
except ImportError:
    from UserList import UserList
from email.utils import getaddresses, parseaddr


Address = namedtuple('Address', ['display_name', 'address'])


def parse(header):
    """Parse email string using `parseaddr`
    """
    return Address(*parseaddr(header))


def parse_list(header):
    """Parse a emails string using getaddresses.
    """
    return AddressList([header])


class AddressList(UserList):
    """Simple list to encapsulate emails.
    """
    @property
    def addresses(self):
      return [x[1] for x in getaddresses(self.data) if x[1]]
