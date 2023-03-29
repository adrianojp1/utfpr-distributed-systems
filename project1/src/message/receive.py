import pika

def listen(exchange, callback):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange=exchange, exchange_type='fanout')
    result = channel.queue_declare(queue='', exclusive=True)

    queue_name = result.method.queue
    channel.queue_bind(exchange=exchange, queue=queue_name)

    print(f'Listening messages on exchange {exchange}...')

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()
