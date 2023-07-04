import com.fasterxml.jackson.module.kotlin.jacksonObjectMapper
import data.*
import message.Consumer
import message.Producer
import java.util.*
import kotlin.system.exitProcess

class OrderService {
    private val orders = mutableMapOf<Int, Order>()
    private val jsonMapper = jacksonObjectMapper()

    private val shippingRequestsExchange = "shipping-requests"
    private val requestProducer = Producer(shippingRequestsExchange)

    private val shippingsExchange = "shippings"
    private val shippingConsumer = Consumer(shippingsExchange)

    private var orderId = 1

    @Suppress("DuplicatedCode")
    fun run() {
        println("Running OrderService")

        Thread { shippingConsumer.consume(this::consumeShipping) }.start()
        Thread.sleep(500)

        while (true) {
            try {
                menu()
            } catch (ex: Exception) {
                println(ex.stackTraceToString())
                println()
            }
        }
    }

    @Suppress("kotlin:S6611")
    private fun consumeShipping(body: ByteArray) {
        val shipping = jsonMapper.readValue(body, Shipping::class.java)
        println("Received shipping: $shipping")

        val order = orders[shipping.orderId]!!
        val updatedOrder = order.copy(
            shippingId = shipping.id,
            state = if (shipping.state == ShippingState.CONCLUDED) OrderState.CONCLUDED else OrderState.FAILED,
            updatedAt = Date()
        )

        println("Updated order: $updatedOrder")
        orders[shipping.orderId] = updatedOrder
    }

    private fun menu() {
        println("""
            Choose an option:
            1. List orders
            2. Make new order
            3. Exit
            
        """.trimIndent())
        when (readln().toInt()) {
            1 -> listOrders()
            2 -> makeNewOrder()
            3 -> exit()
        }
    }

    private fun listOrders() {
        println("Orders:")
        orders.values.forEach { println(it) }
        println()
    }

    private fun makeNewOrder() {
        println("Enter the product id to order:")

        val productId = readln().toInt()
        val orderId = this.orderId++
        val now = Date()

        val order = Order(orderId, productId, OrderState.PENDING, now, now)
        orders[order.id] = order

        val shippingRequest = ShippingRequest(order.id, order.productId, order.requestedAt)
        val json = jsonMapper.writeValueAsString(shippingRequest)
        requestProducer.publish(json)

        println("""
            New order made: $order
            Shipping request published: $shippingRequest
            
        """.trimIndent())
    }

    private fun exit() {
        println("Exited")
        exitProcess(0)
    }
}

fun main() {
    OrderService().run()
}
