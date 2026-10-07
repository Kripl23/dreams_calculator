from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import EventForm
from .models import Account, Event, add_months


class AddMonthsTests(SimpleTestCase):
    def test_same_day(self):
        self.assertEqual(add_months(date(2026, 1, 15), 1), date(2026, 2, 15))

    def test_clamps_to_month_end(self):
        self.assertEqual(add_months(date(2026, 1, 31), 1), date(2026, 2, 28))

    def test_crosses_year(self):
        self.assertEqual(add_months(date(2026, 11, 30), 3), date(2027, 2, 28))


class ApplyEventsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('user', password='pass')
        self.account = Account.objects.create(
            user=self.user, name='Car', goal=Decimal('1000'))

    def create_event(self, day, amount='100'):
        return Event.objects.create(account=self.account, date=day, amount=Decimal(amount))

    def test_credits_each_passed_occurrence(self):
        self.create_event(date(2026, 1, 31))
        self.account.apply_events(today=date(2026, 3, 30))  # Jan 31, Feb 28; Mar 31 not yet
        self.assertEqual(self.account.balance, Decimal('200'))
        dates = self.account.contributions.order_by('date').values_list('date', flat=True)
        self.assertEqual(list(dates), [date(2026, 1, 31), date(2026, 2, 28)])

    def test_second_visit_credits_only_new_occurrences(self):
        event = self.create_event(date(2026, 1, 31))
        self.account.apply_events(today=date(2026, 3, 30))
        self.account.apply_events(today=date(2026, 3, 30))
        self.assertEqual(self.account.balance, Decimal('200'))
        self.account.apply_events(today=date(2026, 3, 31))
        self.assertEqual(self.account.balance, Decimal('300'))
        event.refresh_from_db()
        self.assertEqual(event.applied_count, 3)
        self.assertEqual(event.next_date, date(2026, 4, 30))

    def test_future_event_credits_nothing(self):
        self.create_event(date(2026, 2, 1))
        self.account.apply_events(today=date(2026, 1, 31))
        self.assertEqual(self.account.balance, 0)

    def test_goal_reached(self):
        self.create_event(date(2026, 1, 1), amount='500')
        self.account.apply_events(today=date(2026, 2, 1))
        self.assertTrue(self.account.goal_reached)

    def test_detail_page_applies_events(self):
        self.create_event(timezone.localdate())
        self.client.force_login(self.user)
        self.client.get(reverse('account_detail', args=[self.account.pk]))
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal('100'))


class EventFormTests(TestCase):
    def test_rejects_past_date(self):
        yesterday = timezone.localdate() - timedelta(days=1)
        form = EventForm(data={'date': yesterday, 'amount': '100'})
        self.assertFalse(form.is_valid())
        self.assertIn('date', form.errors)

    def test_accepts_today(self):
        form = EventForm(data={'date': timezone.localdate(), 'amount': '100'})
        self.assertTrue(form.is_valid())
