import os
import sys
import threading

from message.receive import listen
from events.truck_event import TruckEvent
from events.beans_event import BeansEvent


truck_exchange = 'trucks'
beans_exchange = 'beans'


def trucks_callback(ch, method, properties, body: bytes):
    truck_event_json = body.decode()
    print(f'Truck event received: {truck_event_json}')

    truck_event = TruckEvent.from_json(truck_event_json)
    if truck_event.state == 'ENTERING':
        print(
            f'Truck {truck_event._id} just arrived with {truck_event.load}% of load!'
        )
        print('')

    if truck_event.state == 'LEAVING':
        print(
            f'Truck {truck_event._id} just left with {truck_event.load}% of load!'
        )
        print('')


def beans_callback(ch, method, properties, body: bytes):
    beans_event_json = body.decode()
    print(f'Beans event received: {beans_event_json}')

    beans_event = BeansEvent.from_json(beans_event_json)
    if beans_event.load < 30:
        print(
            f'Beans silo needs to be reloaded! Current load: {beans_event.load}%'
        )
        print('')


def main():
    truck_thread = threading.Thread(
        target=listen, args=(truck_exchange, trucks_callback)
    )
    beans_thread = threading.Thread(
        target=listen, args=(beans_exchange, beans_callback)
    )

    truck_thread.start()
    beans_thread.start()

    truck_thread.join()
    beans_thread.join()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
