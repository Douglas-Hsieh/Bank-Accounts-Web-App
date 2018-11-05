# Tests are project specific

from django.test import TestCase
from django.urls import reverse

from bank_accounts.models import Account
from django.contrib.auth.models import User

import random

# Create your tests here.

# TODO: Implement Users being able to claim accounts (ForeignKey on Accounts tied to Users)
# TODO: Emailing users password resets.


class UserTests(TestCase):
    """
    Testing clients who are logged in as Users.
    """
    def test_user_can_login(self):
        """
        A Client who is a User may login.
        :return:
        """
        user = create_user('username', 'password')
        logged_in = self.client.login(username='username', password='password')
        self.assertEqual(logged_in, True)


class HomeViewTests(TestCase):
    """
    Testing the home page.
    """
    def test_correct_title(self):
        """
        Title of the page is correct.
        :return:
        """
        response = self.client.get(reverse('bank accounts home'))
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
        self.assertQuerysetEqual(response.context['account_list'], ['<Account: Checking Account 1>', '<Account: Savings Account 2>'], ordered=False)


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
    def test_not_authenticated(self):
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

    def test_not_authorized(self):
        # Create users
        user_1 = create_user('user_1', 'password')
        user_2 = create_user('user_2', 'password')
        # Create an Account for a User
        account_1 = create_account(account_type=Account.CHECKING, creator=user_1, holder=user_1, balance=0,
                                   bank=Account.WELLS_FARGO, routing_number=123456789)
        request_url = reverse('bank_accounts:update', kwargs={'pk': account_1.pk})
        # Check Authorization
        self.client.login(username='user_2', password='password')  # Client is now authenticated but not authorized
        response = self.client.get(request_url)
        self.assertEqual(response.status_code, 403)  # Forbidden


class AccountDeleteViewTests(TestCase):
    def test_not_authenticated(self):
        """
        If client is not logged in, then client may not delete an Account.
        :return:
        """
        # Create Account for an User
        user = create_user('username', 'password')
        account = create_account(account_type=Account.CHECKING, creator=user, holder=user, balance=0,
                                 bank=Account.WELLS_FARGO, routing_number=123456789)

        url = reverse('bank_accounts:delete', kwargs={'pk': account.pk})
        response = self.client.get(url)
        self.assertRedirects(response, '%s?next=%s' % (reverse('login'), url))

    def test_not_authorized(self):
        """
        If client does not hold an Account, then he may not delete it.
        :return:
        """
        # Create Account for an User
        user_1 = create_user('user_1', 'password')
        user_2 = create_user('user_2', 'password')
        account_1 = create_account(account_type=Account.CHECKING, creator=user_1, holder=user_1, balance=0,
                                   bank=Account.WELLS_FARGO, routing_number=123456789)

        # Client logins and attempts accesses delete view
        self.client.login(username='user_2', password='password')
        url = reverse('bank_accounts:delete', kwargs={'pk': account_1.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)  # Forbidden


class InternalTransferViewTests(TestCase):

    url = reverse('bank_accounts:internal_transfer')

    def test_not_authenticated(self):
        """
        If User not logged in, he may not make an internal transfer or view the internal transfer form.
        :return:
        """
        user = create_user('username', 'password')

        # Create an Account for a User
        account_1 = create_account(holder=user, balance=100)
        account_2 = create_account(holder=user, balance=100)

        url = reverse('bank_accounts:internal_transfer')

        # Client attempts to view the internal transfer form
        get_response = self.client.get(url)
        # Client redirected to login
        self.assertRedirects(get_response, '%s?next=%s' % (reverse('login'), url))

        # Client attempts to make an internal transfer
        post_response = self.client.post(path=url, data={
            'from_account': account_1.id,
            'to_account': account_2.id,
            'balance': 100})
        # Client redirected to login
        self.assertRedirects(post_response, '%s?next=%s' % (reverse('login'), url))
        # Transfer does not occur
        self.assertEqual(Account.objects.get(pk=account_1.pk).balance, 100)
        self.assertEqual(Account.objects.get(pk=account_2.pk).balance, 100)

    def test_not_authorized(self):
        """
        Users cannot internally transfer funds between Accounts they don't hold.
        :return:
        """
        user_1 = create_user('username_1', 'password')
        user_2 = create_user('username_2', 'password')
        account_1 = create_account(holder=user_1, balance=100)
        account_2 = create_account(holder=user_2, balance=100)
        account_3 = create_account(holder=user_2, balance=100)

        # User logs in
        self.client.login(username='username_1', password='password')

        # User attempts to internally transfer from an Account he holds to an Account he doesn't hold.
        url = reverse('bank_accounts:internal_transfer')
        response = self.client.post(path=url, data={
            'from_account': account_1.id,
            'to_account': account_2.id,
            'balance': 100})
        self.assertEqual(response.status_code, 200)  # OK
        # Transfer does not occur
        self.assertEqual(Account.objects.get(pk=account_1.pk).balance, 100)
        self.assertEqual(Account.objects.get(pk=account_2.pk).balance, 100)

        # User attempts to internally transfer from an Account he doesn't hold to an Account he does hold.
        url = reverse('bank_accounts:internal_transfer')
        response = self.client.post(path=url, data={
            'from_account': account_2.id,
            'to_account': account_1.id,
            'balance': 100})
        self.assertEqual(response.status_code, 200)  # OK
        # Transfer does not occur
        self.assertEqual(Account.objects.get(pk=account_1.pk).balance, 100)
        self.assertEqual(Account.objects.get(pk=account_2.pk).balance, 100)

        # User attempts to internally transfer from an Account he doesn't hold to an Account he doesn't hold
        url = reverse('bank_accounts:internal_transfer')
        response = self.client.post(path=url, data={
            'from_account': account_2.id,
            'to_account': account_3.id,
            'balance': 100})
        self.assertEqual(response.status_code, 200)  # OK
        # Transfer does not occur
        self.assertEqual(Account.objects.get(pk=account_2.pk).balance, 100)
        self.assertEqual(Account.objects.get(pk=account_3.pk).balance, 100)

    def test_valid_transfer(self):
        """
        Users can transfer funds between accounts.
        :return:
        """
        user = create_user('username', 'password')
        account_1 = create_account(account_type=Account.CHECKING, creator=user, holder=user, balance=100,
                                   bank=Account.WELLS_FARGO, routing_number=123456789)
        account_2 = create_account(account_type=Account.SAVINGS, creator=user, holder=user, balance=100,
                                   bank=Account.CHASE, routing_number=987654321)
        self.client.login(username='username', password='password')

        url = reverse('bank_accounts:internal_transfer')

        # User submits the internal transfer form
        response = self.client.post(path=url, data={
            'from_account': account_1.id,
            'to_account': account_2.id,
            'balance': 100})

        self.assertEqual(response.status_code, 200)  # OK

        updated_account_1 = Account.objects.get(pk=account_1.pk)
        updated_account_2 = Account.objects.get(pk=account_2.pk)

        # Transfer is successful
        self.assertEqual(updated_account_1.balance, 0)
        self.assertEqual(updated_account_2.balance, 200)

    def test_not_enough_funds(self):
        """
        Users cannot transfer more funds than they actually have.
        :return:
        """
        user = create_user('username', 'password')
        account_1 = create_account(account_type=Account.CHECKING, creator=user, holder=user, balance=100,
                                   bank=Account.WELLS_FARGO, routing_number=123456789)
        account_2 = create_account(account_type=Account.SAVINGS, creator=user, holder=user, balance=100,
                                   bank=Account.CHASE, routing_number=987654321)
        self.client.login(username='username', password='password')

        url = reverse('bank_accounts:internal_transfer')

        # User submits the internal transfer form
        response = self.client.post(path=url, data={
            'from_account': account_1.id,
            'to_account': account_2.id,
            'balance': 101})

        self.assertEqual(response.status_code, 200)

        updated_account_1 = Account.objects.get(pk=account_1.pk)
        updated_account_2 = Account.objects.get(pk=account_2.pk)

        # Transfer did not occur
        self.assertEqual(updated_account_1.balance, 100)
        self.assertEqual(updated_account_2.balance, 100)

    def test_multiple_transfers(self):
        """
        If User makes multiple internal transfers, then they will be successful.
        :return:
        """
        user = create_user('username', 'password')
        account_1 = create_account(account_type=Account.CHECKING, creator=user, holder=user, balance=1000,
                                   bank=Account.WELLS_FARGO, routing_number=123456789)
        account_2 = create_account(account_type=Account.SAVINGS, creator=user, holder=user, balance=1000,
                                   bank=Account.CHASE, routing_number=987654321)
        self.client.login(username='username', password='password')

        url = reverse('bank_accounts:internal_transfer')

        # User submits multiple forms
        for i in range(0, 1000):
            self.client.post(path=url, data={
                'from_account': account_1.id,
                'to_account': account_2.id,
                'balance': 1})
            self.client.post(path=url, data={
                'from_account': account_2.id,
                'to_account': account_1.id,
                'balance': 1})

        updated_account_1 = Account.objects.get(pk=account_1.pk)
        updated_account_2 = Account.objects.get(pk=account_2.pk)

        # Transfer successful
        self.assertEqual(updated_account_1.balance, 1000)
        self.assertEqual(updated_account_2.balance, 1000)

    def test_no_accounts(self):
        """
        If a User has no Accounts, then we handle it properly.
        :return:
        """
        user = create_user('username', 'password')
        self.client.login(username='username', password='password')

        url = reverse('bank_accounts:internal_transfer')

        # GET
        get_response = self.client.get(url)
        self.assertEqual(get_response.status_code, 200)  # OK

        # POST
        post_response = self.client.post(
            path=url,
            data={
                'from_account': 42,
                'to_account': 43,
                'balance': 100
            }
        )
        self.assertEqual(post_response.status_code, 200)  # OK

    def test_nonexisting_accounts(self):
        """
        If a User attempts to make an internal transfer between Accounts that don't exist, then an appropriate message
        is displayed.
        :return:
        """
        user = create_user('username', 'password')
        self.client.login(username='username', password='password')

        # Create an Account for a User
        account_1 = create_account(holder=user, balance=100)
        account_2 = create_account(holder=user, balance=100)

        url = reverse('bank_accounts:internal_transfer')

        # User attempts to make an internal transfer between nonexisting Accounts
        response = self.client.post(path=url, data={
            'from_account': 42,
            'to_account': 43,
            'balance': 100})

        # Response is handled
        self.assertEqual(response.status_code, 200)  # OK

    def test_non_positive_amount(self):
        """
        If a User attempts to transfer a non-positive amount of funds, then the transfer will not occur.
        :return:
        """
        user = create_user('username', 'password')
        account_1 = create_account(holder=user, balance=100)
        account_2 = create_account(holder=user, balance=100)
        self.client.login(username='username', password='password')

        url = reverse('bank_accounts:internal_transfer')

        # User transfers no funds
        response_1 = self.client.post(path=url, data={
            'from_account': account_1.id,
            'to_account': account_2.id,
            'balance': 0})
        # Transfer failed
        self.assertEqual(response_1.status_code, 200)
        self.assertEqual(Account.objects.get(pk=account_1.pk).balance, 100)
        self.assertEqual(Account.objects.get(pk=account_2.pk).balance, 100)

        # User transfers negative funds
        response_2 = self.client.post(path=url, data={
            'from_account': account_1.id,
            'to_account': account_2.id,
            'balance': -10})
        # Transfer failed
        self.assertEqual(response_2.status_code, 200)
        self.assertEqual(Account.objects.get(pk=account_1.pk).balance, 100)
        self.assertEqual(Account.objects.get(pk=account_2.pk).balance, 100)


class InternalTransferReceiptListViewTests(TestCase):

    url = reverse('bank_accounts:internal_transfer_receipt_list')

    def test_not_authenticated(self):
        response = self.client.get(self.url)
        # User is redirected to login, then come back.
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response=response,
            expected_url='%s?next=%s' % (reverse('login'), self.url)
        )


    # TODO Arexis found a bug
    def test_deleted_account(self):
        """
        If a User deletes account, then internal transfer list view still works.
        :return:
        """
        url = reverse('bank_accounts:internal_transfer_receipt_list')

        # Create User and Accounts
        user = create_user('username', 'password')
        account_1 = create_account(holder=user, balance=100)
        account_2 = create_account(holder=user, balance=100)

        # Login
        self.client.login(username='username', password='password')

        # Internal Transfer
        self.client.post(path=reverse('bank_accounts:internal_transfer'), data={
            'from_account': account_1.pk,
            'to_account': account_2.pk,
            'balance': 100})

        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)  # OK


def create_user(username='username', password='password'):
    new_user = User.objects.create(username=username)
    new_user.set_password(password)
    new_user.save()
    return new_user


def create_account(holder, account_type=None, creator=None, balance=None, bank=None, routing_number=None):
    """
    Saves an Account associated with a User to the database and returns the same Account.
    :param account_type:
    :param creator:
    :param holder: User who holds this Account
    :param balance:
    :param bank:
    :param routing_number:
    :return:
    """
    if account_type is None:
        account_type = random.choice(Account.ACCOUNT_TYPE_CHOICES)
    if creator is None:
        creator = holder.username
    if balance is None:
        balance = random.randint(0, 1000)
    if bank is None:
        bank = random.choice(Account.BANK_CHOICES)
    if routing_number is None:
        routing_number = random.randint(0, 10000000)

    return Account.objects.create(account_type=account_type, creator=creator, holder=holder, balance=balance, bank=bank,
                                  routing_number=routing_number)

