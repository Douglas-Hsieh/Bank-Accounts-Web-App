from django.shortcuts import render

# Create your views here.

from .models import Account
from .forms import AccountForm
from django.views.generic import CreateView


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
    return render(request, 'accounts/create_raw.html')


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
    return render(request, 'accounts/create.html', context)


# TODO: Create a generic class view for account creation
class AccountCreateView(CreateView):  # CreateView is generic view for creating models with forms
    model = Account  # Model we're creating
    form_class = AccountForm  # Django Form class we're using
    template_name = 'accounts/create.html'
    success_url = '/accounts/create'  # Upon a successful form submission




