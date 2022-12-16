#!/usr/bin/env python
from argparse import ArgumentParser
import json
import eero
import six

class CookieStore(eero.SessionStorage):
    def __init__(self, cookie_file):
        from os import path
        self.cookie_file = path.abspath(cookie_file)

        try:
            with open(self.cookie_file, 'r') as f:
                self.__cookie = f.read()
        except IOError:
            self.__cookie = None

    @property
    def cookie(self):
        return self.__cookie

    @cookie.setter
    def cookie(self, cookie):
        self.__cookie = cookie
        with open(self.cookie_file, 'w+') as f:
            f.write(self.__cookie)


session = CookieStore('session.cookie')
eero = eero.Eero(session)


def print_json(data):
    print(json.dumps(data, indent=4))


if __name__ == '__main__':
    if eero.needs_login():
        parser = ArgumentParser()
        parser.add_argument("-l", help="your eero login (email address or phone number)")
        args = parser.parse_args()
        if args.l:
            phone_number = args.l
        else:
            phone_number = six.moves.input('your eero login (email address or phone number): ')
        user_token = eero.login(phone_number)
        verification_code = six.moves.input('verification key from email or SMS: ')
        eero.login_verify(verification_code, user_token)
        print('Login successful. Rerun this command to get some output')
    else:
        account = eero.account()

        parser = ArgumentParser()
        parser.add_argument("command",
                            choices=['account', 'devices', 'details', 'info', 'eeros',
                                     'reboot', 'reservations'],
                            help="info to print")
        parser.add_argument("--eero", type=int, help="eero to reboot")
        parser.add_argument("--network", default=None, help="Name or ID of network. Default: return a list of results for all networks")
        args = parser.parse_args()

        if args.command == 'account':
            results = account
        else:
            network_name = args.network
            network_ids = []
            results = []
            for network in account['networks']['data']:
                if network_name is None or network['name'] == network_name or network['url'].rsplit('/', 1)[-1] == network_name:
                    result = None
                    if args.command == 'info':
                        result = network
                    elif args.command == 'details':
                        result = eero.networks(network['url'])
                    elif args.command == 'devices':
                        result = eero.devices(network['url'])
                    elif args.command == 'eeros':
                        result = eero.eeros(network['url'])
                    elif args.command == 'reservations':
                        result = eero.reservations(network['url'])
                    elif args.command == 'reboot':
                        result = eero.reboot(args.eero)
                    if not result is None:
                        results.append(result);
        print_json(results)
