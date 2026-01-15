import sqlite3

DB_NAME = "store.db"

def get_db():
    return sqlite3.connect(DB_NAME, timeout=5, check_same_thread=False)

def init_db():
    db = get_db()
    cur = db.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS Customer (
        CustomerID INTEGER PRIMARY KEY AUTOINCREMENT,
        FirstName TEXT NOT NULL,
        LastName TEXT NOT NULL,
        MiddleName TEXT NOT NULL UNIQUE,
        Telephone TEXT NOT NULL UNIQUE,
        Email TEXT NOT NULL UNIQUE,
        Address TEXT
    );

    CREATE TABLE IF NOT EXISTS Seller (
        SellerID INTEGER PRIMARY KEY AUTOINCREMENT,
        FullName TEXT NOT NULL,
        Phone TEXT UNIQUE,
        Position TEXT
    );

    CREATE TABLE IF NOT EXISTS Configuration (
        ConfigurationID INTEGER PRIMARY KEY AUTOINCREMENT,
        Processor TEXT NOT NULL,
        RAM TEXT NOT NULL,
        Storage TEXT NOT NULL,
        GPU TEXT,
        OS TEXT
    );

    CREATE TABLE IF NOT EXISTS Computer (
        ComputerID INTEGER PRIMARY KEY AUTOINCREMENT,
        Model TEXT NOT NULL,
        Price REAL NOT NULL,
        ConfigurationID INTEGER NOT NULL,
        Warranty INTEGER DEFAULT 12,
        FOREIGN KEY (ConfigurationID)
            REFERENCES Configuration(ConfigurationID)
    );

    CREATE TABLE IF NOT EXISTS OrderTable (
        OrderID INTEGER PRIMARY KEY AUTOINCREMENT,
        OrderDate TEXT NOT NULL,
        CustomerID INTEGER NOT NULL,
        SellerID INTEGER NOT NULL,
        TotalAmount REAL NOT NULL DEFAULT 0,
        FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID),
        FOREIGN KEY (SellerID) REFERENCES Seller(SellerID)
    );

    CREATE TABLE IF NOT EXISTS OrderDetail (
        DetailID INTEGER PRIMARY KEY AUTOINCREMENT,
        OrderID INTEGER NOT NULL,
        ComputerID INTEGER NOT NULL,
        Quantity INTEGER NOT NULL CHECK (Quantity > 0),
        UnitPrice REAL NOT NULL,
        FOREIGN KEY (OrderID) REFERENCES OrderTable(OrderID),
        FOREIGN KEY (ComputerID) REFERENCES Computer(ComputerID)
    );
    """)

    db.commit()
    db.close()
