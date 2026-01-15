from pydantic import BaseModel

class CustomerCreate(BaseModel):
    first_name: str
    last_name: str
    middle_name: str
    telephone: str
    email: str
    address: str | None = None

class SellerCreate(BaseModel):
    full_name: str
    phone: str | None = None
    position: str | None = None

class ConfigurationCreate(BaseModel):
    processor: str
    ram: str
    storage: str
    gpu: str | None = None
    os: str | None = None

class ComputerCreate(BaseModel):
    model: str
    price: float
    configuration_id: int
    warranty: int = 12

class OrderCreate(BaseModel):
    customer_id: int
    seller_id: int

class OrderItemCreate(BaseModel):
    computer_id: int
    quantity: int
