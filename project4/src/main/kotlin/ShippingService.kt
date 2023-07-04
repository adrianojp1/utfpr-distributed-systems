import com.fasterxml.jackson.module.kotlin.jacksonObjectMapper
import data.*
import message.Consumer
import message.Producer
import java.util.*
import kotlin.system.exitProcess

class ShippingService {
    private val products = mutableMapOf<Int, Int>()
    private val shippings = mutableMapOf<Int, Shipping>()
    private val jsonMapper = jacksonObjectMapper()

    private val shippingsExchange = "shippings"
    private val shippingProducer = Producer(shippingsExchange)

    private val shippingRequestsExchange = "shipping-requests"
    private val requestConsumer = Consumer(shippingRequestsExchange)

    private var shippingId = 1

    private var forceErrorOnConsumer = false

    @Suppress("DuplicatedCode")
    fun run() {
        println("Running ShippingService")

        Thread { requestConsumer.consume(this::consumeShippingRequest, this::rollback) }.start()
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

    private fun consumeShippingRequest(body: ByteArray, changeLog: MutableList<Change>) {
        val request = jsonMapper.readValue(body, ShippingRequest::class.java)
        println("Received shipping: $request")

        val productId = request.productId
        val productCount = products[productId]
        val productCanBeShipped = productCount != null && productCount > 0

        changeLog.add(Change("shippingId", null, this.shippingId))
        val shippingId = this.shippingId++

        val now = Date()
        val shipping = Shipping(
            id = shippingId,
            orderId = request.orderId,
            productId = productId,
            state = if (productCanBeShipped) ShippingState.CONCLUDED else ShippingState.FAILED,
            requestedAt = request.requestedAt,
            shippedAt = now
        )

        if (productCanBeShipped) {
            changeLog.add(Change("product", productId, productCount!!))
            products[productId] = productCount - 1
            println("Product id $productId subtracted from stock")
        }

        changeLog.add(Change("shipping", shippingId, shippings[shippingId]))
        shippings[shippingId] = shipping

        if (forceErrorOnConsumer) {
            throw Exception("ShippingService - consumer error")
        }
        println("Order shipped: $shipping")
        shippingProducer.publish(jsonMapper.writeValueAsString(shipping))
    }

    @Suppress("kotlin:S6531")
    private fun rollback(changeLog: List<Change>) {
        println("Rolling back changes")
        changeLog.reversed().forEach { change ->
            when (change.entityType) {
                "shippingId" -> this.shippingId = change.oldValue as Int

                "product" -> products[change.entityId!!] = change.oldValue as Int

                "shipping" -> {
                    if (change.oldValue == null) {
                        shippings.remove(change.entityId)
                    } else {
                        shippings[change.entityId!!] = change.oldValue as Shipping
                    }
                }
            }
        }
    }

    private fun menu() {
        println(
            """
            Choose an option:
            1. List shipping's
            2. List products
            3. Update product count
            4. Toggle force error on consumer
            5. Exit
            
            """.trimIndent()
        )
        when (readln().toInt()) {
            1 -> listShippings()
            2 -> listProducts()
            3 -> updateProductCount()
            4 -> toggleForceErrorOnConsumer()
            5 -> exit()
        }
    }

    private fun listShippings() {
        println("Shipping's:")
        shippings.values.forEach { println(it) }
        println()
    }

    private fun listProducts() {
        println("Products:")
        products.forEach { (id, count) -> println("Product id: $id, stock count: $count") }
        println()
    }

    private fun updateProductCount() {
        println("Enter a product id and it stock count")
        val (productId, count) = readln().split(" ")
        products[productId.toInt()] = count.toInt()
        println()
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
    ShippingService().run()
}
