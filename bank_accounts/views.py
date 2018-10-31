from django.shortcuts import render, reverse, redirect
from django.utils import timezone

# Create your views here.

from .models import Account, InternalTransferReceipt
from django.contrib.auth.models import User

from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, Http404

from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView

from .forms import AccountForm, AccountUpdateForm, InternalTransferForm
from django.contrib.auth.forms import UserCreationForm

# Authentication (i.e. Checking if a client is also a User)

# We can bind the ability to access a view to the authentication of a User

from django.contrib.auth.decorators import login_required  # Use for function based views
# @login_required
# def my_view(request):

from django.contrib.auth.mixins import LoginRequiredMixin  # Use for class based views
# class MyView(LoginRequiredMixin, View):


def home_view(request):
    return render(request, 'home.html')


class UserCreateView(CreateView):  # CreateView indicates creation of object in database (using forms)
    form_class = UserCreationForm  # Format of the form
    template_name = 'registration/signup.html'  # Template that uses the form to display user interface
    success_url = 'accounts/login'


class AccountCreateView(LoginRequiredMixin, CreateView):  # CreateView is generic view for creating models with forms
    model = Account  # Model we're creating
    form_class = AccountForm  # Django Form class we're using
    template_name = 'bank_accounts/create.html'
    # The URL that handles forms typically also displays the form
    success_url = '/bank_accounts/create'  # URL to redirect after user successfully submits form.

# Uses Django's form.ModelForm to handle form processing
# def account_create_view(request):
#
#     form = AccountForm(request.POST or None)
#
#     if form.is_valid():
#         form.save()  # save model to database
#         form = AccountForm()
#
#     context = {
#         'form': form
#     }
#
#     # Using the information of this HTTP request, send a resource (such as a template) with context
#     return render(request, 'bank_accounts/create.html', context)


# User is submitting or viewing Account update form
# Uses raw html instead of Django to implement forms in the template
# def account_create_raw_view(request):
#     """
#     Similar to account_create_view, but implemented without Django forms. Unsafe, as it doesn't perform form validation.
#     :param request:
#     :return:
#     """
#     # If the form has been filled out
#     if request.method == 'POST':
#         # The form describes the properties of the new account.
#         account_type = request.POST.get('type')
#         account_owner = request.POST.get('owner')
#         account_balance = 0
#         account_bank = request.POST.get('bank')
#         account_routing_number = request.POST.get('routing_number')
#
#         # Save the account onto the database.
#         Account.objects.create(type=account_type, owner=account_owner, balance=account_balance, bank=account_bank,
#                                routing_number=account_routing_number)
#
#     # Return an empty form
#     return render(request, 'bank_accounts/create_raw.html')

@login_required
def account_update_view(request, pk):
    # An User is authorized if he is updating an Account he holds
    try:
        account_requested = Account.objects.get(pk=pk)
    except Account.DoesNotExist:
        return Http404()

    if request.user == account_requested.holder:  # Authorized User wishes to submit or view update form for an Account

        if request.method == 'POST':  # User submits form
            form = AccountUpdateForm(request.POST)
            print("POST Request")
            if form.is_valid():  # Submitted form is valid
                print("Valid Form")
                # Process form data
                account_requested.account_type = form.cleaned_data['account_type']
                account_requested.save()
                # Return to Account details
                return redirect(to=reverse('bank_accounts:account_detail', kwargs={'pk': account_requested.pk}))

            else:  # Submitted form is invalid
                print("Invalid Form")
                form = AccountUpdateForm(instance=account_requested)
        else:  # User views form
            print("Not POST Request")
            form = AccountUpdateForm(instance=account_requested)

        context = {'form': form}
        return render(request=request, template_name='bank_accounts/update.html', context=context)

    else:  # Unauthorized
        return HttpResponseForbidden()
# An Authorized User for this view is a User that also holds the Account
# Problem: How do I implement Authorization in a class based view?
# class AccountUpdateView(LoginRequiredMixin, UpdateView):  # Update Account database objects
#     # Authorization check
#
#     model = Account
#     fields = ['account_type']
#     template_name = 'bank_accounts/update.html'
#     # pk_url_kwarg = 'pk'  # The name of the URLConfig keyword argument that contains the primary key.
#
#     def form_valid(self, form):  # called when User submits valid form
#         account = form.save(commit=False)
#         account.updated_by = self.request.user
#         account.updated_at = timezone.now()
#         account.save()
#         return redirect(to=reverse('bank_accounts:account_detail', kwargs={'pk': account.pk}))


@login_required
def account_delete_view(request, pk):
    try:
        account_requested = Account.objects.get(pk=pk)
    except Account.DoesNotExist:
        return Http404

    # Check Authorization
    if request.user == account_requested.holder:
        if request.POST:  # User submit delete form
            # Delete Account
            account_requested.delete()
            return redirect(to=reverse('bank_accounts:account_list'))

        else:  # User views the deletion form
            context = {'account': account_requested}
            return render(request, 'bank_accounts/delete.html', context)
    else:
        return HttpResponseForbidden()  # Unauthorized
# class AccountDeleteView(LoginRequiredMixin, DeleteView):  # Users may delete Accounts they hold
#     model = Account
#     template_name = 'bank_accounts/delete.html'
#     success_url = reverse('bank_accounts:account_list')


# If User is not authenticated, then we URL redirect to login (default is auth login view)
# Display a list of a User's Accounts
class AccountListView(LoginRequiredMixin, ListView):
    template_name = 'bank_accounts/account_list.html'
    model = Account
    context_object_name = 'account_list'

    def get_queryset(self):  # Get the list of model instances we can display
        return Account.objects.filter(holder=self.request.user)


# Custom account detail view that enforces: Only Authenticated, Account holders may view an Account's details
@login_required
def account_detail_view(request, pk):
    # Access the account we want to detail
    try:
        account = Account.objects.get(pk=pk)
    except Account.DoesNotExist:  # Model class supports DNE exceptions
        raise Http404()

    context = {
        "account": account
    }

    # If User holds the Account, User may view Account details
    if request.user == account.holder:
        return render(request=request, template_name='bank_accounts/account_detail.html', context=context)
    # Else User is not Authorized to view resource
    else:
        return HttpResponseForbidden()
# DetailView expects an ID (from URL parameter) associated to the model instance
# class AccountDetailView(LoginRequiredMixin, DetailView):
#     template_name = 'bank_accounts/account_detail.html'
#     model = Account
#     context_object_name = 'account'

    # def get_queryset(self):  # Get list of model instances used as context
    #     return Account.objects.get(holder=self.request.user)  # User can access his own accounts


# TODO: Refreshing causes User to resubmit form. Make sure to redirect them and make them do a GET request right after.
# TODO: Implement an optional message and timestamp for each internal transfer
# TODO: Breaks when User has no Accounts
@login_required
def internal_transfer_view(request):
    # Retrieve a list of User's Accounts
    accounts = Account.objects.filter(holder=request.user)

    # TODO: Test for no Accounts
    if not accounts:  # User has no Accounts
        return render(request, 'home.html', {'message': 'Error: No Accounts to transfer between.'})

    if request.method == 'POST':  # User submitted form
        # Process form
        form = InternalTransferForm(request.POST)
        if form.is_valid():
            try:
                from_account = Account.objects.get(pk=form.cleaned_data['from_account'])
                to_account = Account.objects.get(pk=form.cleaned_data['to_account'])
                amount = form.cleaned_data['balance']
            except Account.DoesNotExist:
                return render(request, 'bank_accounts/account_list.html',
                              {'account_list': accounts,
                               'message': 'Error: Accounts selected invalid.'})

            # Check enough funds to make transfer
            if amount > from_account.balance:
                return render(request, 'bank_accounts/account_list.html',
                              {'account_list': accounts,
                               'message': 'Error: Not enough funds to make transfer.'})

            # Check transfer is between valid accounts
            account_pks = []
            for account in accounts:
                account_pks.append(account.pk)
            if from_account.pk not in account_pks or to_account.pk not in account_pks:
                return render(request, 'bank_accounts/account_list.html',
                              {'account_list': accounts,
                               'message': 'Error: Accounts selected invalid.'})

            # Check transfer is not between the same accounts
            if from_account.pk == to_account.pk:
                return render(request, 'bank_accounts/account_list.html',
                              {'account_list': accounts,
                               'message': 'Error: Selected Accounts cannot be the same.'})

            # Check that transferred funds is positive
            if amount <= 0:
                return render(request, 'bank_accounts/account_list.html',
                              {'account_list': accounts,
                               'message': 'Error: Amount to transfer must be positive.'})

            # Perform transfer
            # TODO: Worry about atomicity of transaction
            from_account.balance = from_account.balance - amount
            to_account.balance = to_account.balance + amount
            from_account.save()
            to_account.save()

            # Save receipt
            InternalTransferReceipt.objects.create(user=request.user,
                                                   from_account=from_account,
                                                   to_account=to_account, amount=amount)

            # Redirect to account list
            return render(request, 'bank_accounts/account_list.html', {'account_list': accounts,
                                                                       'message': "Internal transfer successful."})

        else:  # User submitted invalid form
            return render(request, 'bank_accounts/account_list.html', {'account_list': accounts,
                                                                       'message': "Error: Invalid form data."})

    else:  # User is viewing form
        # Internal Transfers take place between two of a User's Accounts
        return render(request, 'bank_accounts/internal_transfer.html', {'accounts': accounts})
# Uses Raw HTML instead of Django ModelForm. Doesn't support form validation.
# @login_required
# def raw_internal_transfer_view(request):
#     # Retrieve a list of User's Accounts
#     accounts = Account.objects.filter(holder=request.user)
#
#     if request.method == 'POST':  # User submitted form
#
#         # TODO: Validate our data
#         # Process form
#         from_account = Account.objects.get(pk=request.POST.get('from_account'))
#         to_account = Account.objects.get(pk=request.POST.get('to_account'))
#         amount = int(request.POST.get('balance'))
#
#         # Check validity of transfer
#         if amount > from_account.balance:  # Not enough money to transfer
#             return render(request, 'bank_accounts/account_list.html',
#                           {'message': 'Error: Not enough funds to make transfer.'})
#
#         # Perform transfer
#         # TODO: Worry about atomicity of transaction
#         from_account.balance = from_account.balance - amount
#         to_account.balance = to_account.balance + amount
#
#         from_account.save()
#         to_account.save()
#
#         # Redirect to account list
#         return render(request, 'bank_accounts/account_list.html', {'message': "Internal transfer successful."})
#
#     else:  # User is viewing form
#         if not accounts:  # User has no Accounts
#             return Http404  # TODO Do I want this behavior?
#         else:
#             context = {'accounts': accounts}
#             # Internal Transfers take place between two of a User's Accounts
#             return render(request, 'bank_accounts/internal_transfer.html', context)


# TODO: View internal transfer history

class InternalTransferReceiptList(LoginRequiredMixin, ListView):
    template_name = 'bank_accounts/internal_transfer_receipt_list.html'
    model = InternalTransferReceipt
    context_object_name = 'receipts'

    def get_queryset(self):  # Get the list of model instances we can display
        return InternalTransferReceipt.objects.filter(user=self.request.user)


# def internal_transfer_receipt_list_view(request):
#     pass


# User is a making a payment to another User
@login_required
def external_transfer_view(request):
    pass




# TODO: External Transfer



# TODO: Hosting on Heroku/Firebase



