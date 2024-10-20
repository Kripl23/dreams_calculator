from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .models import Account
from .forms import AccountForm, ContributionForm


@login_required
def account_list(request):
    accounts = Account.objects.filter(user=request.user)
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


@login_required
def account_detail(request, pk):
    account = get_object_or_404(Account, pk=pk, user=request.user)
    contributions = account.contributions.order_by('-date')
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
    context = {
        'account': account,
        'contributions': contributions,
        'form': form,
    }
    return render(request, 'financial_tracker/account_detail.html', context)
