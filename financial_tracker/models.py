from calendar import monthrange

from django.db import models, transaction
from django.contrib.auth.models import User
from django.utils import timezone


def add_months(day, months):
    """Shift date by months, clamping to the month end (Jan 31 + 1 -> Feb 28)."""
    month_index = day.month - 1 + months
    year, month = day.year + month_index // 12, month_index % 12 + 1
    return day.replace(year=year, month=month, day=min(day.day, monthrange(year, month)[1]))


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

    def apply_events(self, today=None):
        """Turn every event occurrence that came due since the last visit into a contribution."""
        today = today or timezone.localdate()
        with transaction.atomic():
            for event in self.events.select_for_update():
                due_dates = event.due_dates(today)
                if not due_dates:
                    continue
                Contribution.objects.bulk_create(
                    Contribution(account=self, date=due_date, amount=event.amount)
                    for due_date in due_dates
                )
                self.update_balance(event.amount * len(due_dates))
                event.applied_count += len(due_dates)
                event.save(update_fields=['applied_count'])


class Contribution(models.Model):
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="contributions")
    date = models.DateField(default=timezone.localdate)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self) -> str:
        return f'{self.date} - {self.amount} for {self.account.name}'


class Event(models.Model):
    """Recurring contribution: repeats monthly on the day of `date`."""
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="events")
    created_at = models.DateTimeField(auto_now_add=True)
    date = models.DateField(
        help_text='First occurrence, then repeats monthly on the same day')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    # how many occurrences are already credited to the account
    applied_count = models.PositiveIntegerField(default=0)

    def __str__(self) -> str:
        return f'{self.amount} monthly from {self.date} for {self.account.name}'

    @property
    def next_date(self):
        return add_months(self.date, self.applied_count)

    def occurrences_until(self, day):
        """How many occurrences happened from `date` up to `day` inclusive."""
        if day < self.date:
            return 0
        months = (day.year - self.date.year) * 12 + day.month - self.date.month
        if add_months(self.date, months) > day:
            months -= 1
        return months + 1

    def due_dates(self, today):
        """Dates of occurrences up to today that aren't credited yet."""
        return [add_months(self.date, k)
                for k in range(self.applied_count, self.occurrences_until(today))]
