import pika


def send_msg(exchange, msg):

    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost')
    )
    channel = connection.channel()

    channel.exchange_declare(exchange=exchange, exchange_type='fanout')

    channel.basic_publish(
        exchange=exchange,
        routing_key='',
        body=msg
    )
    print(f"Event sent to exchange. exchange: {exchange}, message '{msg}'")
    connection.close()
