#!/usr/bin/env python3
import sys
import pika

def main():
    usage_msg = 'Usage: receive.py {exchange-name} {message-content}'
    if len(sys.argv) == 1:
        print('A exchange name and message content must be provided!')
        print(usage_msg)
        sys.exit(1)
    elif len(sys.argv) == 2:
        print('A message content must be provided!')
        print(usage_msg)
        sys.exit(2)

    exchange_name = sys.argv[1]
    message = ' '.join(sys.argv[2:])

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange=exchange_name, exchange_type='fanout')

    channel.basic_publish(
        exchange=exchange_name,
        routing_key='',
        body=message
    )
    print(f"Message sent to exchange. exchange: {exchange_name}, message '{message}'")
    connection.close()


if __name__ == '__main__':
    main()