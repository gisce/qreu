# coding=utf-8
from qreu.address import parse, parse_list, AddressList, Address
from expects import *


with description('address module'):
    with context('parsing an address string'):
        with it('must return and object with display_name and address attribute'):
            r = parse('Firstname Secondname <user@example.com>')
            expect(r).to(have_property('address', 'user@example.com'))
            expect(r).to(have_property('display_name', 'Firstname Secondname'))

        with it('must have a display with a formatted address as on creation'):
            addr_str = '"Firstname Secondname" <user@example.com>'
            r = parse(addr_str)
            expect(r).to(have_property('display', addr_str))
            addr_str = 'user@example.com'
            r = parse(addr_str)
            expect(r).to(have_property('display', addr_str))
            addr_str = '      user@example.com        '
            r = parse(addr_str)
            expect(r).to(have_property('display', addr_str.strip()))

        with it('must be able to parse from the class Adress'):
            addr_str = 'Firstname Secondname <user@example.com>'
            r = parse(addr_str)
            expect(r).to(equal(Address.parse(addr_str)))

        with it('must parse multiple addresses'):
            r = parse_list('First <f@example.com>, Second <s@example.com>')
            expect(r).to(be_a(AddressList))
            expect(r).to(have_property('addresses', ['f@example.com', 's@example.com']))

        with it('can sum AddressList'):
            a1 = AddressList(['User <u@example.com>'])
            a2 = AddressList(['User2 <u2@example.com>'])

            expect((a1 + a2).addresses).to(contain_exactly(
                'u@example.com', 'u2@example.com'
            ))
