from django.shortcuts import render


def home_view(request):
    """
    User views home page
    :param request:
    :return:
    """
    return render(request, 'home.html')

def contact_view(request):
    """
    Contact page
    :param request:
    :return:
    """
    return render(request, 'contact.html')
