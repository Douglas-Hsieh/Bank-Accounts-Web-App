# Tests are project specific

from django.test import TestCase
from django.urls import reverse

from bank_accounts.models import Account
from django.contrib.auth.models import User

# Create your tests here.

# TODO: User authentication with bank_accounts. Implement users being able to access only bank_accounts they've created.
    # TODO: Implement Users being able to claim accounts (ForeignKey on Accounts tied to Users)
# TODO: Emailing users password resets.


class HomeViewTests(TestCase):
    """
    Testing the home page.
    """
    def test_correct_title(self):
        """
        Title of the page is correct.
        :return:
        """
        response = self.client.get(reverse('bank_accounts:home'))
        self.assertIs(response.status_code, 200)
        self.assertContains(response, '<title>\nAccounts Home\n</title>')


class AccountListViewTests(TestCase):

    def test_not_authenticated(self):
        """
        If user is not authenticated, he is redirected to login. After login, he can come back.
        :return:
        """
        # TODO: Find out why assertIs doesn't work
        request_url = reverse('bank_accounts:account_list')
        response = self.client.get(request_url)
        # User is redirected to login, then come back.
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response=response,
            expected_url='%s?next=%s' % (reverse('login'), request_url)
        )

    def test_no_accounts(self):
        """
        If an authenticated User has no Accounts, then no Accounts are displayed.
        :return:
        """
        # Create a User and login
        create_user()
        self.client.login(username='new_user', password='12345')  # login as a User
        response = self.client.get(reverse('bank_accounts:account_list'))  # Access the view

        self.assertIs(response.status_code, 200)  # OK
        self.assertQuerysetEqual(response.context['account_list'], [])  # no Accounts

    def test_two_accounts(self):
        """
        If a User has created two Accounts, they will be displayed.
        :return:
        """
        # Create a User
        new_user = create_user()
        # Create two Accounts held by the User
        create_account(account_type=Account.CHECKING, creator='Creator 1', holder=new_user, balance=100,
                       bank=Account.CHASE, routing_number=123456789)
        create_account(account_type=Account.SAVINGS, creator='Creator 2', holder=new_user, balance=200,
                       bank=Account.WELLS_FARGO, routing_number=987654321)
        # Login User
        self.client.login(username='new_user', password='12345')
        # User views his Account list
        response = self.client.get(reverse('bank_accounts:account_list'))

        self.assertIs(response.status_code, 200)  # OK
        # User can view his Accounts
        self.assertQuerysetEqual(response.context['account_list'], ['<Account: 1>', '<Account: 2>'], ordered=False)


class AccountDetailViewTests(TestCase):
    pass


def create_user():
    new_user = User.objects.create(username='new_user')
    new_user.set_password('12345')
    new_user.save()
    return new_user


def create_account(account_type, creator, holder, balance, bank, routing_number):
    """
    Saves an Account to the database and returns the same Account
    :param account_type:
    :param creator:
    :param holder:
    :param balance:
    :param bank:
    :param routing_number:
    :return:
    """
    return Account.objects.create(account_type=account_type, creator=creator, holder=holder, balance=balance, bank=bank,
                                  routing_number=routing_number)




