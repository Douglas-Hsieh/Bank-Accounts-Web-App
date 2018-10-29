# Tests are project specific

from django.test import TestCase
from django.urls import reverse

from bank_accounts.models import Account
from django.contrib.auth.models import User

# Create your tests here.

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

    def test_not_authorized(self):
        """
        If a user doesn't hold an Account, it will not be listed to him.
        :return:
        """
        # Create users
        user_1 = create_user('user_1', '12345')
        user_2 = create_user('user_2', '12345')

        # Create an Account for a User
        account_1 = create_account(account_type=Account.CHECKING, creator=user_1, holder=user_1, balance=0,
                                   bank=Account.WELLS_FARGO, routing_number=123456789)

        # User login and view their account list
        self.client.login(username='user_2', password='12345')
        response = self.client.get(reverse('bank_accounts:account_list'))

        # Test if an Account is displayed to a User who doesn't hold it.
        self.assertEqual(response.status_code, 200)  # User accessed account list page OK
        self.assertNotEqual(user_2, account_1.holder)  # User doesn't hold Account
        # User doesn't see the Account of a another User on his account list
        self.assertNotContains(response, reverse('bank_accounts:account_detail', kwargs={'pk': account_1.pk}))

    def test_no_accounts(self):
        """
        If an authenticated User has no Accounts, then no Accounts are displayed.
        :return:
        """
        # Create a User and login
        new_user = create_user('new_user', '12345')
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
        new_user = create_user('new_user', '12345')
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
    def test_not_authenticated(self):
        """
            If user is not authenticated, he is redirected to login. After login, he can come back.
            :return:
        """
        # Create User
        user = create_user(username='username', password='password')
        # Create Account
        account = create_account(account_type=Account.CHECKING, creator=user, holder=user, balance=0,
                                 bank=Account.WELLS_FARGO, routing_number=123456789)
        # Connect to Account Detail
        request_url = reverse('bank_accounts:account_detail', kwargs={"pk": account.pk})
        response = self.client.get(request_url)

        # User is redirected to login, then come back.
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response=response,
            expected_url='%s?next=%s' % (reverse('login'), request_url)
        )

    def test_not_authorized(self):
        """
        If User doesn't hold this Account, then User cannot view Account details.
        :return:
        """
        # Create users
        user_1 = create_user('user_1', '12345')
        user_2 = create_user('user_2', '12345')

        # Create an Account for a User
        account_1 = create_account(account_type=Account.CHECKING, creator=user_1, holder=user_1, balance=0,
                                   bank=Account.WELLS_FARGO, routing_number=123456789)

        # User logins
        self.client.login(username='user_2', password='12345')
        # User attempts to view account detail of an Account he doesn't hold
        response = self.client.get(reverse('bank_accounts:account_detail',
                                           kwargs={'pk': account_1.pk})
                                   )

        # Implementation #1: User is forbidden to access the page
        self.assertEqual(response.status_code, 403)  # Forbidden

        # Implementation #2: User is redirected to login page
        # self.assertEqual(response.status_code, 200)  # OK
        # self.assertRedirects(response, reverse('login'), 200)  # Successfully redirected to login page


class AccountCreateViewTests(TestCase):
    def test_not_authenticated(self):
        """
        If client is not logged in as User, then client may not create an Account without logging in.
        :return:
        """
        request_url = reverse('bank_accounts:create')
        # Client attempts to create an account
        response = self.client.get(request_url)
        # Client is redirected to login and come back.
        self.assertRedirects(
            response=response,
            expected_url='%s?next=%s' % (reverse('login'), request_url)
        )


class AccountUpdateViewTests(TestCase):
    def test_not_authenticated_or_authorized(self):
        """
        If client not logged in, then client may not update an Account.
        If User does not hold an Account, he may not update it.
        :return:
        """
        # Create users
        user_1 = create_user('user_1', 'password')
        user_2 = create_user('user_2', 'password')
        # Create an Account for a User
        account_1 = create_account(account_type=Account.CHECKING, creator=user_1, holder=user_1, balance=0,
                                   bank=Account.WELLS_FARGO, routing_number=123456789)
        request_url = reverse('bank_accounts:update', kwargs={'pk': account_1.pk})

        # Check Authentication
        response = self.client.get(request_url)
        self.assertRedirects(response, expected_url='%s?next=%s' % (reverse('login'), request_url))

        # Check Authorization
        self.client.login(username='user_2', password='password')  # Client is now authenticated but not authorized
        response = self.client.get(request_url)
        self.assertEqual(response.status_code, 403)  # Forbidden


def create_user(username, password):
    new_user = User.objects.create(username=username)
    new_user.set_password(password)
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
