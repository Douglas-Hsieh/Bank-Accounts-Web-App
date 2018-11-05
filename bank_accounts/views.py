from django.shortcuts import render, reverse, redirect
from django.utils import timezone

# Create your views here.

from .models import Account, InternalTransferReceipt, ExternalTransferReceipt
from django.contrib.auth.models import User

from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, Http404

from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView

from .forms import AccountForm, AccountUpdateForm, InternalTransferForm, ExternalTransferForm
from django.contrib.auth.forms import UserCreationForm

# Authentication (i.e. Checking if a client is also a User)

# We can bind the ability to access a view to the authentication of a User

from django.contrib.auth.decorators import login_required  # Use for function based views
# @login_required
# def my_view(request):

from django.contrib.auth.mixins import LoginRequiredMixin  # Use for class based views
# class MyView(LoginRequiredMixin, View):

from django.contrib import messages


@login_required
def home_view(request):
    """
    Displays home page.
    :param request:
    :return:
    """
    return render(request, 'bank_accounts/home.html')


class UserCreateView(CreateView):  # CreateView indicates creation of object in database (using forms)
    """
    Handles creation of new Users
    """
    form_class = UserCreationForm  # Format of the form
    template_name = 'registration/signup.html'  # Template that uses the form to display user interface
    success_url = 'accounts/login'


class AccountCreateView(LoginRequiredMixin, CreateView):  # CreateView is generic view for creating models with forms
    """
    Handles creation of new bank accounts.
    """
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
    """
    Handles updating information about a bank account.
    :param request:
    :param pk:
    :return:
    """
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
    """
    Displays and processes requests to delete a bank account.
    :param request:
    :param pk:
    :return:
    """
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
    """
    Displays a list of bank accounts.
    """
    template_name = 'bank_accounts/account_list.html'
    model = Account
    context_object_name = 'account_list'

    def get_queryset(self):  # Get the list of model instances we can display
        return Account.objects.filter(holder=self.request.user)


# Custom account detail view that enforces: Only Authenticated, Account holders may view an Account's details
@login_required
def account_detail_view(request, pk):
    """
    Displays details about a specific bank account.
    :param request:
    :param pk:
    :return:
    """
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
@login_required
def internal_transfer_view(request):
    """
    Handles the display and processing of internal transfer form.
    :param request:
    :return:
    """
    # Retrieve a list of User's Accounts
    accounts = Account.objects.filter(holder=request.user)

    if not accounts:  # User has no Accounts
        return render(request, 'bank_accounts/home.html', {'message': 'Error: No Accounts to transfer between.'})

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
            from_account.withdraw(amount)
            to_account.deposit(amount)

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


class InternalTransferReceiptList(LoginRequiredMixin, ListView):
    """
    Displays a history of internal transfers.
    """
    template_name = 'bank_accounts/internal_transfer_receipt_list.html'
    model = InternalTransferReceipt
    context_object_name = 'receipts'

    def get_queryset(self):  # Get the list of model instances we can display
        return InternalTransferReceipt.objects.filter(user=self.request.user)


@login_required
def external_transfer_view(request):
    """
    Handles the display and processing of external transfer form.
    :param request:
    :return:
    """

    # Get list of requesting User's Accounts
    from_accounts = Account.objects.filter(holder=request.user)
    # TODO: What if there are 1 million Users?
    # Get list of all Users
    users = User.objects.all()

    if not from_accounts:  # User has no Accounts
        return render(request, 'bank_accounts/home.html', {'message': 'Error: No Accounts to payments from.'})
    if not users:
        return render(request, 'bank_accounts/home.html', {'message': 'Error: No Users to make payments to.'})

    if request.method == 'GET':  # User views form
        return render(request, 'bank_accounts/external_transfer.html', {'from_accounts': from_accounts,
                                                                        'users': users})
    elif request.method == 'POST':  # User submits form
        form = ExternalTransferForm(request.POST)
        print(form)
        if form.is_valid():

            print('valid')
            # Use form data to get relevant database objects
            try:
                from_account = Account.objects.get(pk=form.cleaned_data['from_account'])
            except Account.DoesNotExist:
                messages.add_message(request, messages.ERROR,
                                     'The account you are making the payment from does not exist.')
                return redirect(to=reverse('bank_accounts:home'))

            try:
                payee = User.objects.get(pk=form.cleaned_data['payee'])
            except User.DoesNotExist:
                messages.add_message(request, messages.ERROR,
                                     'The user you are making the payment to does not exist.')
                return redirect(to=reverse('bank_accounts:home'))

            try:
                payee_accounts = Account.objects.filter(holder=payee.pk)
            except Account.DoesNotExist:
                messages.add_message(request, messages.ERROR,
                                     'The user you are making the payment to does not have any accounts.')
                return redirect(to=reverse('bank_accounts:home'))

            to_account = None
            # for account in payee.account_set:
            for account in payee_accounts:  # For each user account
                if account.account_type == Account.CHECKING:
                    to_account = account
                    break
            if to_account is None:
                messages.add_message(request, messages.ERROR,
                                     'The user you are making the payment to does not have a checking account.')
                return redirect(to=reverse('bank_accounts:home'))

            amount = form.cleaned_data['amount']

            comment = form.cleaned_data['comment']

            # Check valid payment
            if amount > from_account.balance:  # Not enough funds
                messages.add_message(request, messages.ERROR, 'Not enough funds.')
                return redirect(to=reverse('bank_accounts:home'))
            if amount <= 0:  # Non-positive amount
                messages.add_message(request, messages.ERROR, 'You must select a positive amount.')
                return redirect(to=reverse('bank_accounts:home'))
            if request.user == payee:  # Payee is User himself
                messages.add_message(request, messages.ERROR, 'You cannot pay yourself.')
                return redirect(to=reverse('bank_accounts:home'))
            if from_account.account_type != Account.CHECKING:  # from account is not a Checking Account
                messages.add_message(request, messages.ERROR, 'You must make a payment from a checking account.')
                return redirect(to=reverse('bank_accounts:home'))

            # Perform transfer
            # TODO: Worry about atomicity of transaction
            from_account.withdraw(amount)
            to_account.deposit(amount)

            # Save receipt
            ExternalTransferReceipt.objects.create(payer=request.user,
                                                   payee=payee,
                                                   from_account=from_account,
                                                   to_account=to_account,
                                                   comment=comment,
                                                   amount=amount)

            messages.add_message(request, messages.SUCCESS, 'Payment successful.')
            return redirect(reverse('bank_accounts:home'))
        else:  # Invalid form
            messages.add_message(request, messages.ERROR, 'Invalid form.')
            return redirect(reverse('bank_accounts:home'))
    else:  # User makes some other request
        # Treat it as GET request
        messages.add_message(request, messages.ERROR, 'Unrecognized request.')
        return render(request, 'bank_accounts/external_transfer.html', {'from_accounts': from_accounts,
                                                                        'users': users})


class ExternalTransferReceiptList(LoginRequiredMixin, ListView):
    """
    Displays a history of external transfers.
    """
    template_name = 'bank_accounts/external_transfer_receipt_list.html'
    model = ExternalTransferReceipt
    context_object_name = 'receipts'

    def get_queryset(self):  # Get the list of model instances we can display
        return ExternalTransferReceipt.objects.filter(payer=self.request.user) |\
               ExternalTransferReceipt.objects.filter(payee=self.request.user)


# TODO: Learn Django Concurrency



