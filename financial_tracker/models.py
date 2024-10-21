from django.db import models
from django.contrib.auth.models import User


class Account(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="accounts")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    goal = models.DecimalField(max_digits=12, decimal_places=2)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    goal_reached = models.BooleanField(default=False)
    # TODO create multiple curencies

    def __str__(self):  # pylint: disable=E0307
        return self.name

    def update_balance(self, amount):
        self.balance += amount
        if self.balance >= self.goal:
            self.goal_reached = True
        self.save()


class Contribution(models.Model):
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="contributions")
    date = models.DateField(auto_now_add=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self) -> str:
        return f'{self.date} - {self.amount} for {self.account.name}'
