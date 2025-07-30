# coding: utf-8
from __future__ import absolute_import, unicode_literals

from collections import namedtuple

import six

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
            return '"{display_name}" <{address}>'.format(**self._asdict())
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


def normalize_display_address(addr_string):
    """
    Ensures that the display name in an email address is properly quoted
    if it contains special characters. If a display name is present before
    a '<...>' address block and is not already quoted, it will be quoted.

    :param addr_string: A string containing a full email address
                        (e.g. RAMOS ESCOLÀ, PEPITA <pepita@example.com>)
    :return: A normalized email string with quoted display name if needed
    """
    if isinstance(addr_string, six.binary_type):
        addr_string = addr_string.decode('utf-8')
    if '<' in addr_string and '>' in addr_string:
        name_part, addr_part = addr_string.split('<', 1)
        name = name_part.strip()
        email = addr_part.strip('> ').strip()

        special_chars = {',', ';', '<', '>'}
        if name and not (name.startswith('"') and name.endswith('"')) and any(char in name for char in special_chars):
            name = name.replace('"', r'\"')
            if any(c in name for c in [',', ';', ':']):
                name = '"{}"'.format(name)

        return '{} <{}>'.format(name, email)
    return addr_string  # If no angle brackets found, return as-is

