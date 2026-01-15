from fastapi import FastAPI, HTTPException
from datetime import date

from store.db import get_db, init_db

from store.models import (
        CustomerCreate,
        SellerCreate,
        ConfigurationCreate,
        ComputerCreate,
        OrderCreate,
        OrderItemCreate
        )

app = FastAPI(
        title="PC Store API",
        docs_url="/docs",
        redoc_url="/redoc"
        )

init_db()

# Customers

@app.post("/customers")
def create_customer(c: CustomerCreate):
    db = get_db()
    cur = db.cursor()
    try:
        cur.execute("""
            INSERT INTO Customer
            (FirstName, LastName, MiddleName, Telephone, Email, Address)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (c.first_name, c.last_name, c.middle_name,
              c.telephone, c.email, c.address))
        db.commit()
        return {"status": "customer created"}
    except Exception:
        raise HTTPException(400, "Customer already exists")
    finally:
        db.close()

@app.get("/customers")
def get_customers():
    db = get_db()
    cur = db.cursor()

    cur.execute("""
        SELECT CustomerID, FirstName, LastName, Telephone, Email
        FROM Customer
    """)
    rows = cur.fetchall()
    db.close()

    return [
        {
            "customer_id": r[0],
            "first_name": r[1],
            "last_name": r[2],
            "telephone": r[3],
            "email": r[4],
        }
        for r in rows
    ]

# Sellers

@app.post("/sellers")
def create_seller(s: SellerCreate):
    db = get_db()
    cur = db.cursor()
    cur.execute("""
        INSERT INTO Seller (FullName, Phone, Position)
        VALUES (?, ?, ?)
    """, (s.full_name, s.phone, s.position))
    db.commit()
    db.close()
    return {"status": "seller created"}

@app.get("/sellers")
def get_sellers():
    db = get_db()
    cur = db.cursor()

    cur.execute("""
        SELECT SellerID, FullName, Phone, Position
        FROM Seller
    """)
    rows = cur.fetchall()
    db.close()

    return [
        {
            "seller_id": r[0],
            "full_name": r[1],
            "phone": r[2],
            "position": r[3],
        }
        for r in rows
    ]

# Configuration

@app.post("/configurations")
def create_configuration(cfg: ConfigurationCreate):
    db = get_db()
    cur = db.cursor()
    cur.execute("""
        INSERT INTO Configuration (Processor, RAM, Storage, GPU, OS)
        VALUES (?, ?, ?, ?, ?)
    """, (cfg.processor, cfg.ram, cfg.storage, cfg.gpu, cfg.os))
    config_id = cur.lastrowid
    db.commit()
    db.close()
    return {"configuration_id": config_id}

@app.get("/configurations")
def get_configurations():
    db = get_db()
    cur = db.cursor()

    cur.execute("""
        SELECT ConfigurationID, Processor, RAM, Storage, GPU, OS
        FROM Configuration
    """)
    rows = cur.fetchall()
    db.close()

    return [
        {
            "configuration_id": r[0],
            "processor": r[1],
            "ram": r[2],
            "storage": r[3],
            "gpu": r[4],
            "os": r[5],
        }
        for r in rows
    ]

# Computer

@app.post("/computers")
def create_computer(c: ComputerCreate):
    db = get_db()
    cur = db.cursor()
    cur.execute("""
        INSERT INTO Computer
        (Model, Price, ConfigurationID, Warranty)
        VALUES (?, ?, ?, ?)
    """, (c.model, c.price, c.configuration_id, c.warranty))
    db.commit()
    db.close()
    return {"status": "computer added"}

@app.get("/computers")
def get_computers():
    db = get_db()
    cur = db.cursor()

    cur.execute("""
        SELECT
            comp.ComputerID,
            comp.Model,
            comp.Price,
            comp.Warranty,
            cfg.Processor,
            cfg.RAM,
            cfg.Storage,
            cfg.GPU,
            cfg.OS
        FROM Computer comp
        JOIN Configuration cfg
            ON comp.ConfigurationID = cfg.ConfigurationID
    """)
    rows = cur.fetchall()
    db.close()

    return [
        {
                "computer_id": r[0],
                "model": r[1],
                "price": r[2],
                "warranty": r[3],
                "processor": r[4],
                "ram": r[5],
                "storage": r[6],
                "gpu": r[7],
                "os": r[8],
        }
        for r in rows
    ]

# Orders

@app.post("/orders")
def create_order(o: OrderCreate):
    db = get_db()
    cur = db.cursor()
    cur.execute("""
        INSERT INTO OrderTable (OrderDate, CustomerID, SellerID)
        VALUES (?, ?, ?)
    """, (date.today().isoformat(), o.customer_id, o.seller_id))
    order_id = cur.lastrowid
    db.commit()
    db.close()
    return {"order_id": order_id}

@app.post("/orders/{order_id}/items")
def add_item(order_id: int, item: OrderItemCreate):
    db = get_db()
    cur = db.cursor()

    cur.execute(
            "SELECT Price FROM Computer WHERE ComputerID = ?",
            (item.computer_id,)
            )
    row = cur.fetchone()
    if not row:
        raise HTTPException(404, "Computer not found")

    unit_price = row[0]

    cur.execute("""
        INSERT INTO OrderDetail
        (OrderID, ComputerID, Quantity, UnitPrice)
        VALUES (?, ?, ?, ?)
    """, (order_id, item.computer_id, item.quantity, unit_price))

    cur.execute("""
        UPDATE OrderTable
        SET TotalAmount = (
            SELECT SUM(Quantity * UnitPrice)
            FROM OrderDetail
            WHERE OrderID = ?
        )
        WHERE OrderID = ?
    """, (order_id, order_id))

    db.commit()
    db.close()
    return {"status": "item added"}

@app.get("/orders/{order_id}")
def get_order(order_id: int):
    db = get_db()
    cur = db.cursor()

    cur.execute("""
        SELECT o.OrderID, o.OrderDate, o.TotalAmount,
               c.FirstName || ' ' || c.LastName
        FROM OrderTable o
        JOIN Customer c ON o.CustomerID = c.CustomerID
        WHERE o.OrderID = ?
    """, (order_id,))
    order = cur.fetchone()

    if not order:
        raise HTTPException(404, "Order not found")

    cur.execute("""
        SELECT comp.Model, d.Quantity, d.UnitPrice
        FROM OrderDetail d
        JOIN Computer comp ON d.ComputerID = comp.ComputerID
        WHERE d.OrderID = ?
    """, (order_id,))
    items = cur.fetchall()

    db.close()

    return {
            "order": {
                "id": order[0],
                "date": order[1],
                "total": order[2],
                "customer": order[3]
                },
            "items": [
                {"model": i[0], "quantity": i[1], "unit_price": i[2]}
                for i in items
                ]
            }
