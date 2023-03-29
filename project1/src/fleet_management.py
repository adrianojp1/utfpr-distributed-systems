import os
import sys

from message.receive import listen
from events.truck_event import TruckEvent


exchange = 'trucks'

on_farm_trucks = set()
out_farm_trucks = set()


def trucks_callback(ch, method, properties, body: bytes):
    truck_event_json = body.decode()
    print(f'Truck event received: {truck_event_json}')

    truck_event = TruckEvent.from_json(truck_event_json)
    if truck_event.state == 'ENTERING':
        on_farm_trucks.add(truck_event._id)
        out_farm_trucks.discard(truck_event._id)

    if truck_event.state == 'LEAVING':
        out_farm_trucks.add(truck_event._id)
        on_farm_trucks.discard(truck_event._id)

    print('Current trucks:')
    print(f'Trucks on farm: {list(on_farm_trucks)}')
    print(f'Trucks out of farm: {list(out_farm_trucks)}')


def main():
    listen(exchange, trucks_callback)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
