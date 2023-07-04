package data

data class Change(
    val entityType: String,
    val entityId: Int?,
    val oldValue: Any?
)
