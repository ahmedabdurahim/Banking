import sqlite3

# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect('database.db')

# Create a cursor object to execute SQL statements
cursor = conn.cursor()


def CreateUser(email, password, first_name, last_name, bankid, bankacc, balance):

    # Create the users table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            password TEXT,
            first_name TEXT,
            last_name TEXT,
            bankid TEXT,
            bankacc TEXT,
            balance TEXT
        )
    ''')

    cursor.execute('SELECT email FROM users WHERE email = ?', (email,))
    existing_email = cursor.fetchone()

    if existing_email is not None:
        # Email already exists, return False
        return False
    else:
        # Execute an INSERT statement to create a new user record
        cursor.execute('''
            INSERT INTO users (email, password, first_name, last_name, bankid, bankacc, balance)
            VALUES (:email, :password, :first_name, :last_name, :bankid, :bankacc, :balance)
        ''', {'email': email, 'password': password, 'first_name': first_name, 'last_name': last_name, 'bankid': bankid, 'bankacc': bankacc, 'balance':balance})

        # Commit the changes to the database
        conn.commit()
        return True


def CreateBank(name, address, date):
    # Create the banks table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS banks (
            bank_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            address TEXT,
            date TEXT
        )
    ''')

    # Insert data into the banks table
    cursor.execute('''
        INSERT INTO banks (name, address, date)
        VALUES (:name, :address, :date)
    ''', {'name': name, 'address': address, 'date': date})

    # Commit the changes to the database
    conn.commit()
    return True


def CreateBankEntity(bank_id, email, password, first_name, last_name, transactions_access, executive_access, users_access):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bank_entities (
            email TEXT PRIMARY KEY,
            bank_id INTEGER,
            password TEXT,
            first_name TEXT,
            last_name TEXT,
            transactions_access TEXT,
            executive_access TEXT,
            users_access TEXT
        )
    ''')

    # Check if the user with the given email already exists
    cursor.execute('SELECT email FROM bank_entities WHERE email = ?', (email,))
    existing_user = cursor.fetchone()

    if existing_user:
        # User with the given email already exists
        return False

    # Insert data into the bank_entities table
    cursor.execute('''
        INSERT INTO bank_entities (bank_id, email, password, first_name, last_name, transactions_access, executive_access, users_access)
        VALUES (:bank_id, :email, :password, :first_name, :last_name, :transactions_access, :executive_access, :users_access)
    ''', {'bank_id': bank_id, 'email': email, 'password': password, 'first_name': first_name, 'last_name': last_name, 'transactions_access': transactions_access, 'executive_access':executive_access, 'users_access': users_access})

    # Commit the changes to the database
    conn.commit()
    return True


def CreateTransaction(bank_id, transaction_id, account_no, debitcredit, date, status):
    # Create the transactions table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            bank_id INTEGER,
            transaction_id INTEGER PRIMARY KEY,
            account_no TEXT,
            debitcredit REAL,
            date TEXT,
            status TEXT
        )
    ''')

    # Check if the account exists in the users table
    cursor.execute('''
        SELECT * FROM users WHERE account_no = :account_no AND bank_id = :bank_id
    ''', {'account_no': account_no, 'bank_id': bank_id})

    user = cursor.fetchone()

    if user:
        # Retrieve the existing balance
        current_balance = user[3]  # Assuming the balance column is at index 3

        # Calculate the updated balance
        updated_balance = current_balance + debitcredit

        # Update the balance in the users table
        cursor.execute('''
            UPDATE users SET balance = :updated_balance WHERE account_no = :account_no AND bank_id = :bank_id
        ''', {'updated_balance': updated_balance, 'account_no': account_no, 'bank_id': bank_id})

    # Insert data into the transactions table
    cursor.execute('''
        INSERT INTO transactions (bank_id, transaction_id, account_no, debitcredit, date, status)
        VALUES (:bank_id, :transaction_id, :account_no, :debitcredit, :date, :status)
    ''', {'bank_id': bank_id, 'transaction_id': transaction_id, 'account_no': account_no, 'debitcredit': debitcredit, 'date': date, 'status': status})

    # Commit the changes to the database
    conn.commit()



print(CreateBankEntity(1, 'email@email.com','12345678','Fname','Lname', 'READWRITE', 'READWRITE', 'READWRITE'))


