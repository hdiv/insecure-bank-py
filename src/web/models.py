from django.db import models


class ModelSerializationMixin(object):
    def as_dict(self) -> dict:
        data = {}
        for field in self._meta.fields:
            value = getattr(self, field.name)
            data[field.name] = value
        return data

    def from_dict(self, values: dict):
        for key, value in values.items():
            setattr(self, key, value)


class Account(models.Model):
    username = models.CharField(primary_key=True, max_length=80)
    name = models.CharField(max_length=80)
    surname = models.CharField(max_length=80)
    password = models.CharField(max_length=80)


class CashAccount(models.Model):
    number = models.CharField(max_length=80)
    username = models.CharField(max_length=80)
    description = models.CharField(max_length=80)
    availableBalance = models.FloatField()


class CreditAccount(models.Model):
    cashAccountId = models.IntegerField()
    number = models.CharField(max_length=80)
    username = models.CharField(max_length=80)
    description = models.CharField(max_length=80)
    availableBalance = models.FloatField()


class Transfer(models.Model, ModelSerializationMixin):
    fromAccount = models.CharField(max_length=80)
    toAccount = models.CharField(max_length=80)
    description = models.CharField(max_length=80)
    amount = models.FloatField()
    fee = models.FloatField(default=20)
    username = models.CharField(max_length=80)
    date = models.DateTimeField()


class Transaction(models.Model):
    number = models.CharField(max_length=80)
    description = models.CharField(max_length=80)
    amount = models.FloatField()
    availableBalance = models.FloatField()
    date = models.DateTimeField()
