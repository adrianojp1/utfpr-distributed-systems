package data

import java.util.*

data class Shipping(
    val id: Int,
    val orderId: Int,
    val productId: Int,
    val state: ShippingState,
    val requestedAt: Date,
    val shippedAt: Date
)
