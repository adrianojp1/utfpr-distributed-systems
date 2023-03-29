import os
import re
import sys

from message.send import send_msg
from events.beans_event import BeansEvent


exchange = 'beans'


def print_usage():
    print('Enter {silo load: in %}')
    print("Enter 'help' to show this message again")
    print('')


def main():
    print_usage()
    r = re.compile('\d{1,3}%')

    while True:
        ipt = input()

        if ipt.strip() == '':
            continue

        elif ipt == 'help':
            print_usage()
            continue

        elif not r.match(ipt):
            print('Wrong arguments format')
            print_usage()
            continue

        silo_load = int(ipt[:-1])
        beans_event = BeansEvent(silo_load)
        send_msg(exchange, beans_event.to_json())


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
