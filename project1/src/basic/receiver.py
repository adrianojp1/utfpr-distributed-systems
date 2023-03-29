#!/usr/bin/env python3
import os
import sys
import pika

def callback(ch, method, properties, body):
    print("Received %s" % body)

def main():
    if len(sys.argv) == 1:
        print('A exchange name must be provided!')
        print('Usage: receive.py {exchange-name}')
        sys.exit(1)

    exchange_name = sys.argv[1]
    
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange=exchange_name, exchange_type='fanout')
    result = channel.queue_declare(queue='', exclusive=True)

    queue_name = result.method.queue
    channel.queue_bind(exchange=exchange_name, queue=queue_name)

    print(f'Listening messages on exchange {exchange_name}. To exit press CTRL+C')

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
