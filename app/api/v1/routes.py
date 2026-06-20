from fastapi import APIRouter, HTTPException, Path, status

from app.models.customer import Customer
from app.services.customers import get_customer_by_id

router = APIRouter(tags=["customers"])


@router.get("/customers/{customerId}", response_model=Customer)
async def read_customer(
    customerId: str = Path(
        min_length=1,
        description="Customer identifier",
    )
) -> Customer:
    customer = get_customer_by_id(customerId)
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer '{customerId}' was not found",
        )
    return customer
