from app.models.customer import Customer


MOCK_CUSTOMERS: dict[str, Customer] = {
    "cust-001": Customer(
        id="cust-001",
        name="Acme Corporation",
        email="security-contact@acme.example",
        status="active",
        plan="enterprise",
    ),
    "cust-002": Customer(
        id="cust-002",
        name="Globex Security",
        email="platform-team@globex.example",
        status="active",
        plan="professional",
    ),
}


def get_customer_by_id(customer_id: str) -> Customer | None:
    return MOCK_CUSTOMERS.get(customer_id)

