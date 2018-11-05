from django.shortcuts import render


def home_view(request):
    """
    User views home page
    :param request:
    :return:
    """
    return render(request, 'home.html')


