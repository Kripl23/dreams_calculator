from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .models import Account, Event
from .forms import AccountForm, ContributionForm, EventForm


@login_required
def account_list(request):
    accounts = Account.objects.filter(user=request.user)
    for account in accounts:
        account.apply_events()
    return render(request, 'financial_tracker/account_list.html', {'accounts': accounts})


@login_required
def add_account(request):
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.user = request.user
            account.save()
            return redirect('account_list')
    else:
        form = AccountForm()
    return render(request, 'financial_tracker/add_account.html', {'form': form})


def render_account_detail(request, account, form=None, event_form=None):
    context = {
        'account': account,
        'contributions': account.contributions.order_by('-date'),
        'events': account.events.order_by('date'),
        'form': form or ContributionForm(),
        'event_form': event_form or EventForm(),
    }
    return render(request, 'financial_tracker/account_detail.html', context)


@login_required
def account_detail(request, pk):
    account = get_object_or_404(Account, pk=pk, user=request.user)
    account.apply_events()
    if request.method == 'POST':
        form = ContributionForm(request.POST)
        if form.is_valid():
            contribution = form.save(commit=False)
            contribution.account = account
            contribution.save()
            account.update_balance(contribution.amount)
            return redirect('account_detail', pk=account.pk)
    else:
        form = ContributionForm()
    return render_account_detail(request, account, form=form)


@login_required
@require_POST
def add_event(request, pk):
    account = get_object_or_404(Account, pk=pk, user=request.user)
    event_form = EventForm(request.POST)
    if event_form.is_valid():
        event = event_form.save(commit=False)
        event.account = account
        event.save()
        return redirect('account_detail', pk=account.pk)
    return render_account_detail(request, account, event_form=event_form)


@login_required
@require_POST
def delete_event(request, pk):
    event = get_object_or_404(Event, pk=pk, account__user=request.user)
    event.delete()
    return redirect('account_detail', pk=event.account_id)
