package message

import com.rabbitmq.client.*
import data.Change

class Consumer(private val exchange: String) {

    private val factory = ConnectionFactory()
    private val connectionName = "amqp://guest:guest@localhost:5672/"

    fun consume(callback: (ByteArray, MutableList<Change>) -> Unit, rollback: (List<Change>) -> Unit) {
        while (true) {
            val changeLog = mutableListOf<Change>()
            try {
                factory.newConnection(connectionName).use { connection ->
                    connection.createChannel().use { channel ->

                        channel.exchangeDeclare(exchange, BuiltinExchangeType.FANOUT)
                        val queue = channel.queueDeclare().queue
                        channel.queueBind(queue, exchange, "")
                        val callbackConsumer = object : DefaultConsumer(channel) {
                            override fun handleDelivery(
                                consumerTag: String,
                                envelope: Envelope,
                                properties: AMQP.BasicProperties,
                                body: ByteArray
                            ) {
                                callback(body, changeLog)
                                channel.basicAck(envelope.deliveryTag, false)
                            }
                        }

                        println("Listening messages on exchange $exchange...")
                        while (true) {
                            channel.basicConsume(queue, false, callbackConsumer)
                        }
                    }
                }
            } catch (ex: Exception) {
                println(ex.stackTraceToString())
                rollback(changeLog)
            }
            Thread.sleep(1000)
        }
    }
}