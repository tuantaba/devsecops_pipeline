from pydantic import BaseModel, EmailStr, Field


class Customer(BaseModel):
    id: str = Field(..., examples=["cust-001"])
    name: str = Field(..., examples=["Acme Corporation"])
    email: EmailStr = Field(..., examples=["security-contact@acme.example"])
    status: str = Field(..., examples=["active"])
    plan: str = Field(..., examples=["enterprise"])

