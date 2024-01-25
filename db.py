import sqlite3
import uuid
import secrets
from datetime import date

# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect('database.db', check_same_thread=False)

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
            balance REAL
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


def CreateBank(name, address):
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
    ''', {'name': name, 'address': address, 'date': date.today()})

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


def CreateTransaction(bank_id, account_no, debitcredit):
    # Create the transactions table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            bank_id TEXT,
            transaction_id TEXT PRIMARY KEY,
            account_no TEXT,
            debitcredit REAL,
            date TEXT,
            status TEXT
        )
    ''')

    # Check if the account exists in the users table
    cursor.execute('''
        SELECT * FROM users WHERE bankacc = :bankacc AND bankid = :bank_id
    ''', {'bankacc': account_no, 'bank_id': bank_id})

    user = cursor.fetchone()

    if user:
        # Retrieve the existing balance
        current_balance = float(user[7])  # Assuming the balance column is at index 6
        if (debitcredit + current_balance < 0):
            return False
        else:
            credit_score = FetchCreditScore(bank_id, account_no)
            calculated_score = CalculateCreditScore(bank_id, account_no, credit_score)
            ModifyCreditScore(bank_id, account_no, calculated_score,8.0)

            # Calculate the updated balance
            updated_balance = current_balance + debitcredit

            # Update the balance in the users table
            cursor.execute('''
                UPDATE users SET balance = :updated_balance WHERE bankacc = :account_no AND bankid = :bank_id
            ''', {'updated_balance': updated_balance, 'account_no': account_no, 'bank_id': bank_id})

            # Insert data into the transactions table
            cursor.execute('''
                INSERT INTO transactions (bank_id, transaction_id, account_no, debitcredit, date, status)
                VALUES (:bank_id, :transaction_id, :account_no, :debitcredit, :date, :status)
            ''', {'bank_id': bank_id, 'transaction_id': str(uuid.uuid4()), 'account_no': account_no, 'debitcredit': float(debitcredit), 'date': date.today(), 'status': "COMPLETE"})

            # Commit the changes to the database
            conn.commit()

            return True
    else:
        return False


def CreateAPIKEY(bank_id, read_access, write_access):
    api_key = secrets.token_hex(4)
     # Create the api_key table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_key (
            bank_id INTEGER,
            read_access INTEGER,
            write_access INTEGER,
            api_key TEXT,
            PRIMARY KEY (api_key)
        )
    ''')

    # Insert the data into the api_key table
    cursor.execute('''
        INSERT INTO api_key (bank_id, read_access, write_access, api_key)
        VALUES (:bank_id, :read_access, :write_access, :api_key)
    ''', {'bank_id': bank_id, 'read_access': read_access, 'write_access': write_access, 'api_key': api_key})

    # Commit the changes and close the connection
    conn.commit()
    return api_key


def CreditScore(bank_id, account_no, credit_score, interest_rate):
    # Create the credit_score table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS credit_score (
            bank_id INTEGER,
            account_no TEXT,
            credit_score INTEGER,
            interest_rate REAL,
            PRIMARY KEY (bank_id, account_no)
        )
    ''')

    # Insert the data into the credit_score table
    cursor.execute('''
        INSERT INTO credit_score (bank_id, account_no, credit_score, interest_rate)
        VALUES (:bank_id, :account_no, :credit_score, :interest_rate)
    ''', {'bank_id': bank_id, 'account_no': account_no, 'credit_score': credit_score, 'interest_rate': interest_rate})

    # Commit the changes and close the connection
    conn.commit()
    return True


def FetchBalance(bank_id, account_no):
    # Execute the query to fetch the balance
    cursor.execute('''
        SELECT balance FROM users
        WHERE bankacc = ? AND bankid = ?
    ''', (account_no, bank_id))

    # Fetch the result
    result = cursor.fetchone()

    # Return the balance if it exists, otherwise return None
    balance = result[0] if result else None
    return balance


def FetchLoan(bank_id, account_no):
    # Execute the query to fetch the balance
    cursor.execute('''
        SELECT loan_amount FROM credit_report
        WHERE account_no = ? AND bank_id = ?
    ''', (account_no, bank_id))

    # Fetch the result
    result = cursor.fetchone()

    # Return the balance if it exists, otherwise return None
    balance = result[0] if result else None

    return balance


def FetchCreditScore(bank_id, account_no):
    # Execute the query to fetch the balance
    cursor.execute('''
        SELECT credit_score FROM credit_score
        WHERE account_no = ? AND bank_id = ?
    ''', (account_no, bank_id))

    # Fetch the result
    result = cursor.fetchone()

    # Return the balance if it exists, otherwise return None
    credit_score = result[0] if result else None

    return credit_score

def FetchAccountNumber(bank_id, email):
    # Execute the query to fetch the balance
    cursor.execute('''
        SELECT bankacc FROM users
        WHERE bankid = ? AND email = ?
    ''', (bank_id, email))

    # Fetch the result
    result = cursor.fetchone()

    # Return the balance if it exists, otherwise return None
    account_no = result[0] if result else None

    return account_no


def CreditReport(bank_id, account_no, loan_amount):
    # Create the credit_score table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS credit_report (
            bank_id INTEGER,
            account_no TEXT,
            loan_id TEXT,
            loan_amount REAL,
            remaining REAL,
            status TEXT,
            interest_rate REAL,
            date_due TEXT,
            PRIMARY KEY (loan_id)
        )
    ''')

    loan_outstanding = FetchLoan(bank_id, account_no)

    if(loan_outstanding is None):
        credit_score = FetchCreditScore(bank_id, account_no)
        calculated_score = CalculateCreditScore(bank_id, account_no, credit_score)
        ModifyCreditScore(bank_id, account_no, calculated_score, 8.0)

        # Insert the data into the credit_score table
        cursor.execute('''
            INSERT INTO credit_report (bank_id, account_no, loan_id, loan_amount, remaining, status, interest_rate, date_due)
            VALUES (:bank_id, :account_no, :loan_id, :loan_amount, :remaining, :status, :interest_rate, :date_due)
        ''', {'bank_id': bank_id, 'account_no': account_no, 'loan_id': str(uuid.uuid4()), 'loan_amount': loan_amount, 'remaining': loan_amount, 'status': 'OPEN', 'interest_rate': 8.0 ,'date_due' : str(date.today())})

        CreateTransaction(bank_id, account_no, loan_amount)

        # Commit the changes and close the connection
        conn.commit()

        return True 
    else:
        return False


def CalculateCreditScore(bank_id, account_no, current_score):
    balance = FetchBalance(bank_id, account_no)
    loan = FetchLoan(bank_id, account_no) if FetchLoan(bank_id, account_no) is not None else 0

    fraction = (balance - loan)/850
    credit_score = max(min(fraction + current_score, 850), 300)
    

    return credit_score


def ModifyCreditScore(bank_id, account_no, credit_score, interest_rate):
    # Check if the bank_id and account_no exist in the credit_score table
    cursor.execute('''
        SELECT COUNT(*) FROM credit_score
        WHERE bank_id = ? AND account_no = ?
    ''', (bank_id, account_no))

    # Fetch the result
    result = cursor.fetchone()
    exists = result[0] > 0

    if exists:
        # Run the update query to modify the credit score and interest rate
        cursor.execute('''
            UPDATE credit_score
            SET credit_score = ?, interest_rate = ?
            WHERE bank_id = ? AND account_no = ?
        ''', (credit_score, interest_rate, bank_id, account_no))

        # Commit the changes to the database
        conn.commit()

    # Return True if the update was performed, otherwise return False
    return exists


def Login(bank_id, email, password):
    # Execute the query to check if the user exists
    cursor.execute('''
        SELECT COUNT(*) FROM users
        WHERE bankid = ? AND email = ? AND password = ?
    ''', (bank_id, email, password))

    # Fetch the result
    result = cursor.fetchone()[0]

    # Return True if the user exists, False otherwise
    if result > 0:
        return True
    else:
        return False


def StaffLogin(bank_id, email, password):
    # Execute the query to check if the user exists
    cursor.execute('''
        SELECT COUNT(*) FROM bank_entities
        WHERE bank_id = ? AND email = ? AND password = ?
    ''', (bank_id, email, password))

    # Fetch the result
    result = cursor.fetchone()[0]

    # Return True if the user exists, False otherwise
    if result > 0:
        return True
    else:
        return False


def GetTransactions(bank_id, account_no):
     # Execute the query to fetch transactions
    cursor.execute('''
        SELECT * FROM transactions
        WHERE bank_id = ? AND account_no = ?
    ''', (bank_id, account_no))

    # Fetch all rows
    rows = cursor.fetchall()

    # Create a list to store the transactions
    transactions = []

    # Convert each row into a dictionary and append to the transactions list
    for row in rows:
        transaction = {
            'bank_id': row[0],
            'transaction_id': row[1],
            'account_no': row[2],
            'debitcredit': row[3],
            'date': row[4],
            'status': row[5]
        }
        transactions.append(transaction)

    # Return the transactions list
    return transactions




def GetLoans(bank_id, account_no):
     # Execute the query to fetch transactions
    cursor.execute('''
        SELECT * FROM credit_report
        WHERE bank_id = ? AND account_no = ?
    ''', (bank_id, account_no))

    # Fetch all rows
    rows = cursor.fetchall()

    # Create a list to store the transactions
    loans = []

    # Convert each row into a dictionary and append to the transactions list
    for row in rows:
        loan = {
            'bank_id': row[0],
            'account_no': row[1],
            'loan_id': row[2],
            'loan_amount': row[3],
            'remaining': row[4],
            'status': row[5],
            'interest_rate': row[6],
            'date_due': row[7]

        }
        loans.append(loan)

    # Return the transactions list
    return loans


# print(GetLoans('1','100000'))

