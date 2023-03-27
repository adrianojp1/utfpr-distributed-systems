#!/usr/bin/env python3
import sys
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='notifications',
                         exchange_type='fanout')

message = ' '.join(sys.argv[1:]) or "default message: Hello World!"

channel.basic_publish(
    exchange='notifications',
    routing_key='',
    body=message
)
print("Sent '%s'" % message)
connection.close()
