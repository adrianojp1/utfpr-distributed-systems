import os
import sys

from message.receive import listen
from events.beans_event import BeansEvent


exchange = 'beans'

beans_silo_load = 0


def beans_callback(ch, method, properties, body: bytes):
    beans_event_json = body.decode()
    print(f'Beans event received: {beans_event_json}')

    beans_event = BeansEvent.from_json(beans_event_json)
    beans_silo_load = beans_event.load

    print(f'Current beans silo load: {beans_silo_load}')


def main():
    listen(exchange, beans_callback)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
