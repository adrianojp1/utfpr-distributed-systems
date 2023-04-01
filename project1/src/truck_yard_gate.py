import os
import re
import sys

from events.truck_event import TruckEvent
from message.send import send_msg


exchange = 'trucks'


def print_usage():
    print(
        'Enter {truck id} {state: 0 for leaving, 1 for entering} {truck load: in %}'
    )
    print("Enter 'help' to show this message again")
    print('')


def main():
    print_usage()
    r = re.compile('\d+ \d{1} \d{1,3}%')

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

        truck_id_in, state_in, truck_load_in = ipt.split(' ')

        truck_id = int(truck_id_in)
        truck_state = 'ENTERING' if state_in == '1' else 'LEAVING'
        truck_load = int(truck_load_in[:-1])

        truck_event = TruckEvent(truck_id, truck_state, truck_load)
        send_msg(exchange, truck_event.to_json())


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
