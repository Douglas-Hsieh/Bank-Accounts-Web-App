from django.shortcuts import render

# Create your views here.

from .models import Account
from .forms import AccountForm
from django.views.generic import CreateView, ListView, DetailView
from django.contrib.auth.forms import UserCreationForm

# Authentication

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


# TODO: Let users be able to view their own accounts


class AccountListView(ListView):
    template_name = 'bank_accounts/account_list.html'
    model = Account
    context_object_name = 'account_list'

    def get_queryset(self):  # Get the list of model instances we can display
        return Account.objects.filter(holder=self.request.user)


# TODO: If a user has permission, he can view his account

# DetailView expects an ID (from URL parameter) associated to the model instance
class AccountDetailView(DetailView):
    template_name = 'bank_accounts/account_detail.html'
    model = Account
    context_object_name = 'account'

    # def get_queryset(self):  # Get list of model instances used as context
    #     return Account.objects.get(holder=self.request.user)  # User can access his own accounts

