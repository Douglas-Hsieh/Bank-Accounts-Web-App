from django.shortcuts import render, reverse

# Create your views here.

from .models import Account
from .forms import AccountForm
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, Http404
from django.views.generic import CreateView, ListView, DetailView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin

# Authentication (i.e. Checking if a client is also a User)

# We can bind the ability to access a view to the authentication of a User

from django.contrib.auth.decorators import login_required  # Use for function based views
# @login_required
# def my_view(request):

from django.contrib.auth.mixins import LoginRequiredMixin  # Use for class based views
# class MyView(LoginRequiredMixin, View):


def home_view(request):
    return render(request, 'home.html')


# Uses raw html instead of Django to implement forms in the template
def account_create_raw_view(request):

    """
    Similar to account_create_view, but implemented without Django forms. Unsafe, as it doesn't perform form validation.
    :param request:
    :return:
    """
    # If the form has been filled out
    if request.method == 'POST':
        # The form describes the properties of the new account.
        account_type = request.POST.get('type')
        account_owner = request.POST.get('owner')
        account_balance = 0
        account_bank = request.POST.get('bank')
        account_routing_number = request.POST.get('routing_number')

        # Save the account onto the database.
        Account.objects.create(type=account_type, owner=account_owner, balance=account_balance, bank=account_bank,
                               routing_number=account_routing_number)

    # Return an empty form
    return render(request, 'bank_accounts/create_raw.html')


# Uses Django's form.ModelForm to handle form processing
def account_create_view(request):

    form = AccountForm(request.POST or None)

    if form.is_valid():
        form.save()  # save model to database
        form = AccountForm()

    context = {
        'form': form
    }

    # Using the information of this HTTP request, send a resource (such as a template) with context
    return render(request, 'bank_accounts/create.html', context)


class AccountCreateView(CreateView):  # CreateView is generic view for creating models with forms
    model = Account  # Model we're creating
    form_class = AccountForm  # Django Form class we're using
    template_name = 'bank_accounts/create.html'
    success_url = '/bank_accounts/create'  # Upon a successful form submission


class UserCreateView(CreateView):  # CreateView indicates creation of object in database (using forms)
    form_class = UserCreationForm  # Format of the form
    template_name = 'registration/signup.html'  # Template that uses the form to display user interface
    success_url = 'accounts/login'


# Authenticated Users may view Accounts they hold
# If User is not authenticated, then we URL redirect to login (default is auth login view)
class AccountListView(LoginRequiredMixin, ListView):
    template_name = 'bank_accounts/account_list.html'
    model = Account
    context_object_name = 'account_list'

    def get_queryset(self):  # Get the list of model instances we can display
        return Account.objects.filter(holder=self.request.user)


# DetailView expects an ID (from URL parameter) associated to the model instance
# LoginMixin ensures only authenticated Users may call the view


# TODO: Only Authenticated, Account holders may view an Account's details
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


# class AccountDetailView(LoginRequiredMixin, DetailView):
#     template_name = 'bank_accounts/account_detail.html'
#     model = Account
#     context_object_name = 'account'

    # def get_queryset(self):  # Get list of model instances used as context
    #     return Account.objects.get(holder=self.request.user)  # User can access his own accounts
