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

    private var forceErrorOnNewOrder = false
    private var forceErrorOnConsumer = false

    @Suppress("DuplicatedCode")
    fun run() {
        println("Running OrderService")

        Thread { shippingConsumer.consume(this::consumeShipping, this::rollback) }.start()
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
    private fun consumeShipping(body: ByteArray, changeLog: MutableList<Change>) {
        val shipping = jsonMapper.readValue(body, Shipping::class.java)
        println("Received shipping: $shipping")

        val order = orders[shipping.orderId]!!
        val updatedOrder = order.copy(
            shippingId = shipping.id,
            state = if (shipping.state == ShippingState.CONCLUDED) OrderState.CONCLUDED else OrderState.FAILED,
            updatedAt = Date()
        )

        changeLog.add(Change("order", orderId, order))
        orders[shipping.orderId] = updatedOrder

        if (forceErrorOnConsumer) {
            throw Exception("OrderService - consumer error")
        }
        println("Updated order: $updatedOrder")
    }

    @Suppress("kotlin:S6531")
    private fun rollback(changeLog: List<Change>) {
        println("Rolling back changes")
        changeLog.reversed().forEach { change ->
            when (change.entityType) {
                "orderId" -> this.orderId = change.oldValue as Int

                "order" -> {
                    if (change.oldValue == null) {
                        orders.remove(change.entityId)
                    } else {
                        orders[change.entityId!!] = change.oldValue as Order
                    }
                }
            }
        }
    }

    private fun menu() {
        println(
            """
            Choose an option:
            1. List orders
            2. Make new order
            3. Toggle force error on new order
            4. Toggle force error on consumer
            5. Exit
            
        """.trimIndent()
        )
        when (readln().toInt()) {
            1 -> listOrders()
            2 -> makeNewOrder()
            3 -> toggleForceErrorNewOrder()
            4 -> toggleForceErrorOnConsumer()
            5 -> exit()
        }
    }

    private fun listOrders() {
        println("Orders:")
        orders.values.forEach { println(it) }
        println()
    }

    private fun makeNewOrder() {
        val changeLog = mutableListOf<Change>()
        try {
            println("Enter the product id to order:")

            val productId = readln().toInt()

            changeLog.add(Change("orderId", null, this.orderId))
            val orderId = this.orderId++
            val now = Date()

            changeLog.add(Change("order", orderId, null))
            val order = Order(orderId, productId, OrderState.PENDING, now, now)
            orders[order.id] = order

            val shippingRequest = ShippingRequest(order.id, order.productId, order.requestedAt)
            val json = jsonMapper.writeValueAsString(shippingRequest)

            if (forceErrorOnNewOrder) {
                throw Exception("OrderService - new order error")
            }
            requestProducer.publish(json)

            println(
                """
                New order made: $order
                Shipping request published: $shippingRequest
                
                """.trimIndent()
            )
        } catch (ex: Exception) {
            rollback(changeLog)
        }
    }

    private fun toggleForceErrorNewOrder() {
        forceErrorOnNewOrder = !forceErrorOnNewOrder
        println("Force error on new order: $forceErrorOnNewOrder")
    }

    private fun toggleForceErrorOnConsumer() {
        forceErrorOnConsumer = !forceErrorOnConsumer
        println("Force error on consumer: $forceErrorOnConsumer")
    }

    private fun exit() {
        println("Exited")
        exitProcess(0)
    }
}

fun main() {
    OrderService().run()
}
