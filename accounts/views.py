from django.shortcuts import render

# Create your views here.

from .forms import AccountForm


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

