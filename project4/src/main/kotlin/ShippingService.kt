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

    private fun generateShippingId(): Int = if (shippings.isEmpty()) 1 else shippings.keys.max() + 1

    @Suppress("DuplicatedCode")
    fun run() {
        println("Running ShippingService")

        Thread { requestConsumer.consume(this::consumeShippingRequest) }.start()
        Thread.sleep(100)

        while (true) {
            try {
                menu()
            } catch (ex: Exception) {
                println(ex.stackTraceToString())
                println()
            }
        }
    }

    private fun consumeShippingRequest(body: ByteArray) {
        val request = jsonMapper.readValue(body, ShippingRequest::class.java)
        println("Received shipping: $request")

        val productId = request.productId
        val productCount = products[productId]
        val productCanBeShipped = productCount != null && productCount > 0

        val shippingId = generateShippingId()
        val now = Date()
        val shipping = Shipping(
            id = shippingId,
            orderId = request.orderId,
            productId = productId,
            state = if (productCanBeShipped) ShippingState.CONCLUDED else ShippingState.FAILED,
            requestedAt = request.requestedAt,
            shippedAt = now
        )

        productCount?.let { products[productId] = it - 1 }
        shippings[shippingId] = shipping

        println("Order shipped: $shipping")
        shippingProducer.publish(jsonMapper.writeValueAsString(shipping))
    }

    private fun menu() {
        println(
            """
            Choose an option:
            1. List shipping's
            2. List products
            3. Update product count
            4. Exit
            
        """.trimIndent()
        )
        when (readln().toInt()) {
            1 -> listShippings()
            2 -> listProducts()
            3 -> updateProductCount()
            4 -> exit()
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

    private fun exit() {
        println("Exited")
        exitProcess(0)
    }
}

fun main() {
    ShippingService().run()
}
