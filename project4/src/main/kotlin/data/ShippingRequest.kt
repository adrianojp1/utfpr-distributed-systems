package data

import java.util.*

data class ShippingRequest(
    val orderId: Int,
    val productId: Int,
    val requestedAt: Date
)
