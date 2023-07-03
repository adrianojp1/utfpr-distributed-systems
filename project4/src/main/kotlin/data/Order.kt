package data

import java.util.*

data class Order(
    val id: Int,
    val productId: Int,
    val state: OrderState,
    val requestedAt: Date,
    val updatedAt: Date,
    val shippingId: Int? = null
)
