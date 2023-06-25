import sqlite3
from datetime import datetime
import random


class User:
    def __init__(self, id, first_name, last_name, father_name, birth_date, city, phone_number, national_code):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.father_name = father_name
        self.birth_date = birth_date
        self.city = city
        self.phone_number = phone_number
        self.national_code = national_code
        self.registration_date = datetime.now()
        self.accounts = []

    def edit_user_info(self, first_name=None, last_name=None, father_name=None, birth_date=None, city=None, mobile_number=None):
        if first_name:
            self.first_name = first_name
        if last_name:
            self.last_name = last_name
        if father_name:
            self.father_name = father_name
        if birth_date:
            self.birth_date = birth_date
        if city:
            self.city = city
        if mobile_number:
            self.mobile_number = mobile_number

    def delete_account(self, account):
        if account in self.accounts:
            self.accounts.remove(account)

    def view_accounts(self):
        for account in self.accounts:
            print(f"Account Type: {account.account_type}")
            print(f"Account Number: {account.account_number}")
            print(f"Balance: {account.balance}")
            print("-" * 20)


class Account:
    def __init__(self, account_type, balance):
        self.account_type = account_type
        self.account_number = self.generate_account_number()
        self.balance = balance
    
    def generate_account_number(self):
        # Generate a random 8-digit account number
        return str(random.randint(10000000, 99999999))

    def deposit(self, amount):
        self.balance += amount

    def withdraw(self, amount):
        if self.balance < amount:
            print("Insufficient balance")
        else:
            self.balance -= amount
            print("Transaction successful")

class Bank:
    def __init__(self):
        self.users = []

    def connect(self):
        self.conn = sqlite3.connect('bank.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                                first_name TEXT,
                                last_name TEXT,
                                father_name TEXT,
                                birth_date DATE,
                                city TEXT,
                                mobile_number TEXT,
                                national_code TEXT PRIMARY KEY,
                                registration_date DATE)""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS accounts (
                                account_type TEXT,
                                account_number TEXT PRIMARY KEY,
                                balance INTEGER,
                                owner_national_code TEXT,
                                FOREIGN KEY (owner_national_code) REFERENCES users(national_code))""")
        self.conn.commit()

    def close_connection(self):
        self.conn.close()

    def add_user(self, user):
        self.cursor.execute("SELECT * FROM users WHERE national_code=?", (user.national_code,))
        if self.cursor.fetchone():
            print("A user with this national code already exists")
        else:
            self.cursor.execute("""INSERT INTO users (first_name, last_name, father_name, birth_date,
                                    city, mobile_number, national_code, registration_date)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                                    (user.first_name, user.last_name, user.father_name, user.birth_date,
                                    user.city, user.mobile_number, user.national_code, user.registration_date))
            self.conn.commit()
            print("User added successfully")

    def add_account(self, national_code, account_type, balance):
        self.cursor.execute("SELECT * FROM users WHERE national_code=?", (national_code,))
        user = self.cursor.fetchone()
        if user:
            account_number = Account.generate_account_number(self)
            self.cursor.execute("""INSERT INTO accounts (account_type, account_number, balance, owner_national_code)
                                    VALUES (?, ?, ?, ?)""",
                                    (account_type, account_number, balance, national_code))
            self.conn.commit()
            print("Account added successfully")
            return account_number
        else:
            print("User not found")

    def get_user_accounts(self, national_code):
        self.cursor.execute("SELECT * FROM accounts WHERE owner_national_code=?", (national_code,))
        accounts = self.cursor.fetchall()
        return accounts
    
    def account_menu(self, national_code):
        while True:
            print("=" * 30)
            print("Account menu")
            print("1 - View accounts")
            print("2 - Deposit")
            print("3 - Withdraw")
            print("4 - Back")
            choice = input("Select an option: ")
            accounts = self.get_user_accounts(national_code)

            if choice == "1":
                if accounts:
                    print("Your accounts:")
                    for account in accounts:
                        print(f"Account Type: {account[0]}")
                        print(f"Account Number: {account[1]}")
                        print(f"Balance: {account[2]}")
                        print("-" * 20)
                else:
                    print("You have no accounts")

            elif choice == "2":
                if accounts:
                    account_number = input("Enter account number: ")
                    amount = int(input("Enter amount to deposit: "))
                    for account in accounts:
                        if account[1] == account_number:
                            account_obj = Account(account[0], account[2])
                            account_obj.deposit(amount)
                            self.cursor.execute("UPDATE accounts SET balance=? WHERE account_number=?",
                                                (account_obj.balance, account_number))
                            self.conn.commit()
                            print("Deposit successful")
                            break
                    else:
                        print("Account not found")
                else:
                    print("You have no accounts")

            elif choice == "3":
                if accounts:
                    account_number = input("Enter account number: ")
                    amount = int(input("Enter amount to withdraw: "))
                    for account in accounts:
                        if account[1] == account_number:
                            account_obj = Account(account[0], account[2])
                            account_obj.withdraw(amount)
                            self.cursor.execute("UPDATE accounts SET balance=? WHERE account_number=?",
                                                (account_obj.balance, account_number))
                            self.conn.commit()
                            break
                    else:
                        print("Account not found")
                else:
                    print("You have no accounts")

            elif choice == "4":
                break

            else:
                print("Invalid choice")

    def login(self, national_code):
        self.cursor.execute("SELECT * FROM users WHERE national_code=?", (national_code,))
        user = self.cursor.fetchone()
        if user:
            return User(*user)
        else:
            return None

bank = Bank()
bank.connect()

while True:
        print("=" * 30)
        print("Main menu")
        print("1 - Login")
        print("2 - Register")
        print("3 - Exit")
        choice = input("Select an option: ")

        if choice == "1":
            national_code = input("Enter your national code: ")
            user = bank.login(national_code)
            if user:
                print(f"Welcome, {user.first_name} {user.last_name}")
                bank.account_menu(national_code)
            else:
                print("Invalid national code or password")

        elif choice == "2":
            first_name = input("Enter your first name: ")
            last_name = input("Enter your last name: ")
            father_name = input("Enter your father name: ")
            birth_date = input("Enter your birth date (yyyy-mm-dd): ")
            city = input("Enter your city: ")
            mobile_number = input("Enter your mobile number: ")
            national_code = input("Enter your national code: ")
            user = User(first_name, last_name, father_name, birth_date, city, mobile_number, national_code)
            bank.add_user(user)
            account_type = input("Enter account type (e.g. current, savings): ")
            balance = int(input("Enter initial balance: "))
            bank.add_account(national_code, account_type, balance)

        elif choice == "3":
            bank.close()
            print("Goodbye!")
            break

        else:
            print("Invalid choice")