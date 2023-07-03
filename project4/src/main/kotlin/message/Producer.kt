package message

import com.rabbitmq.client.BuiltinExchangeType
import com.rabbitmq.client.ConnectionFactory
import java.nio.charset.StandardCharsets

class Producer(private val exchange: String) {
    private val factory = ConnectionFactory()
    private val connectionName = "amqp://guest:guest@localhost:5672/"

    fun publish(message: String) {
        factory.newConnection(connectionName).use { connection ->
            connection.createChannel().use { channel ->
                channel.exchangeDeclare(exchange, BuiltinExchangeType.FANOUT)
                channel.basicPublish(
                    exchange,
                    "",
                    null,
                    message.toByteArray(StandardCharsets.UTF_8)
                )
            }
        }
    }
}