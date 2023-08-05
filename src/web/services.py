import os

from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.db import connection, transaction
from web.models import (
    Account,
    CashAccount,
    CreditAccount,
    Transaction,
    Transfer,
)


class StorageService:
    folder = os.path.join(settings.BASE_DIR, "web", "static", "resources", "avatars")

    def exists(self, file_name: str) -> bool:
        file = os.path.join(self.folder, file_name)
        return os.path.exists(file)

    def load(self, file_name: str):
        file = os.path.join(self.folder, file_name)
        with open(file, "rb") as fh:
            return fh.read()

    def save(self, data: bytes, file_name: str):
        file = os.path.join(self.folder, file_name)
        with open(file, "wb") as fh:
            fh.write(data)


class AccountService(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        username = request.POST.get("username")
        password = request.POST.get("password")
        accounts = self.find_users_by_username_and_password(username, password)
        if len(accounts) == 0:
            return None
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User(username=username, password=password)
            user.is_staff = True
            user.is_superuser = username == "john"
            user.save()
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    @staticmethod
    def find_users_by_username_and_password(
        username: str, password: str
    ) -> list[Account]:
        sql = (
            "select * from web_account where username='"
            + username
            + "' AND password='"
            + password
            + "'"
        )
        return Account.objects.raw(sql)

    @staticmethod
    def find_users_by_username(username: str) -> list[Account]:
        sql = "select * from web_account where username='" + username + "'"
        return Account.objects.raw(sql)

    @staticmethod
    def find_all_users() -> list[Account]:
        sql = "select * from web_account"
        return Account.objects.raw(sql)


class CashAccountService:
    @staticmethod
    def find_cash_accounts_by_username(username: str) -> list[CashAccount]:
        sql = "select * from web_cashaccount  where username='" + username + "'"
        return CashAccount.objects.raw(sql)

    @staticmethod
    def get_from_account_actual_amount(account: str) -> float:
        sql = "SELECT availableBalance FROM web_cashaccount WHERE number = %s"
        with connection.cursor() as cursor:
            cursor.execute(sql, [account])
            row = cursor.fetchone()
            return row[0]

    @staticmethod
    def get_id_from_number(account: str) -> int:
        sql = "SELECT id FROM web_cashaccount WHERE number = %s"
        with connection.cursor() as cursor:
            cursor.execute(sql, [account])
            row = cursor.fetchone()
            return row[0]


class CreditAccountService:
    @staticmethod
    def find_credit_accounts_by_username(username: str) -> list[CreditAccount]:
        sql = "select * from web_creditaccount  where username='" + username + "'"
        return CreditAccount.objects.raw(sql)

    @staticmethod
    def update_credit_account(cashAccountId: int, round: float):
        sql = (
            "UPDATE web_creditaccount SET availableBalance='"
            + str(round)
            + "' WHERE cashAccountId ='"
            + str(cashAccountId)
            + "'"
        )
        with connection.cursor() as cursor:
            cursor.execute(sql)


class ActivityService:
    @staticmethod
    def find_transactions_by_cash_account_number(number: str) -> list[Transaction]:
        sql = "SELECT * FROM web_transaction WHERE number = '" + number + "'"
        return Transaction.objects.raw(sql)

    @staticmethod
    def insert_new_activity(
        date, description: str, number: str, amount: float, avaiable_balance: float
    ):
        sql = (
            "INSERT INTO web_transaction "
            "(date, description, number, amount, availablebalance) "
            "VALUES (%s, %s, %s, %s, %s)"
        )
        with connection.cursor() as cursor:
            cursor.execute(sql, [date, description, number, amount, avaiable_balance])


class TransferService:
    @staticmethod
    def insert_transfer(transfer: Transfer):
        sql = (
            "INSERT INTO web_transfer "
            "(fromAccount, toAccount, description, amount, fee, username, date) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)"
        )
        with connection.cursor() as cursor:
            cursor.execute(
                sql,
                [
                    transfer.fromAccount,
                    transfer.toAccount,
                    transfer.description,
                    transfer.amount,
                    transfer.fee,
                    transfer.username,
                    transfer.date,
                ],
            )

    @staticmethod
    @transaction.atomic
    def createNewTransfer(transfer: Transfer):
        TransferService.insert_transfer(transfer)

        actual_amount = CashAccountService.get_from_account_actual_amount(
            transfer.fromAccount
        )
        amount_total = actual_amount - (transfer.amount + transfer.fee)
        amount = actual_amount - transfer.amount
        amount_with_fees = amount - transfer.fee
        cash_account_id = CashAccountService.get_id_from_number(transfer.fromAccount)
        CreditAccountService.update_credit_account(
            cash_account_id, round(amount_total, 2)
        )
        desc = (
            transfer.description
            if len(transfer.description) <= 12
            else transfer.description[0:12]
        )
        ActivityService.insert_new_activity(
            transfer.date,
            f"TRANSFER: {desc}",
            transfer.fromAccount,
            -round(transfer.amount, 2),
            round(amount, 2),
        )
        ActivityService.insert_new_activity(
            transfer.date,
            "TRANSFER FEE",
            transfer.fromAccount,
            -round(transfer.fee, 2),
            round(amount_with_fees, 2),
        )

        to_cash_account_id = CashAccountService.get_id_from_number(transfer.toAccount)
        to_actual_amount = CashAccountService.get_from_account_actual_amount(
            transfer.toAccount
        )
        to_amount_total = to_actual_amount + transfer.amount
        CreditAccountService.update_credit_account(
            to_cash_account_id, round(to_amount_total, 2)
        )
        ActivityService.insert_new_activity(
            transfer.date,
            f"TRANSFER: ${desc}",
            transfer.toAccount,
            round(transfer.amount, 2),
            round(to_amount_total, 2),
        )
