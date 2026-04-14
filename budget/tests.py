from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Category, Transaction
import datetime


class AuthTestCase(APITestCase):
    """Helper base class that creates and logs in a test user."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        response = self.client.post(reverse('token_obtain_pair'), {
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')


class CategoryTests(AuthTestCase):

    def test_create_category(self):
        response = self.client.post(reverse('category-list'), {'name': 'Food'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 1)
        self.assertEqual(Category.objects.first().user, self.user)

    def test_list_categories(self):
        Category.objects.create(name='Food', user=self.user)
        Category.objects.create(name='Transport', user=self.user)
        response = self.client.get(reverse('category-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_user_sees_only_own_categories(self):
        other_user = User.objects.create_user(username='other', password='pass123')
        Category.objects.create(name='Other Food', user=other_user)
        Category.objects.create(name='My Food', user=self.user)
        response = self.client.get(reverse('category-list'))
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'My Food')

    def test_unauthenticated_access_denied(self):
        self.client.credentials()
        response = self.client.get(reverse('category-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TransactionTests(AuthTestCase):

    def setUp(self):
        super().setUp()
        self.category = Category.objects.create(name='Food', user=self.user)

    def test_create_income_transaction(self):
        data = {
            'title': 'Salary',
            'amount': '50000.00',
            'type': 'income',
            'date': '2026-01-01',
            'category': self.category.id,
        }
        response = self.client.post(reverse('transaction-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Transaction.objects.count(), 1)

    def test_create_expense_transaction(self):
        data = {
            'title': 'Groceries',
            'amount': '500.00',
            'type': 'expense',
            'date': '2026-01-02',
            'category': self.category.id,
        }
        response = self.client.post(reverse('transaction-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_filter_by_type(self):
        Transaction.objects.create(
            user=self.user, title='Salary', amount=50000,
            type='income', date=datetime.date.today()
        )
        Transaction.objects.create(
            user=self.user, title='Groceries', amount=500,
            type='expense', date=datetime.date.today()
        )
        response = self.client.get(reverse('transaction-list'), {'type': 'income'})
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Salary')

    def test_filter_by_category(self):
        other_category = Category.objects.create(name='Transport', user=self.user)
        Transaction.objects.create(
            user=self.user, title='Bus', amount=50,
            type='expense', date=datetime.date.today(), category=other_category
        )
        Transaction.objects.create(
            user=self.user, title='Groceries', amount=500,
            type='expense', date=datetime.date.today(), category=self.category
        )
        response = self.client.get(
            reverse('transaction-list'), {'category': self.category.id}
        )
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Groceries')

    def test_user_sees_only_own_transactions(self):
        other_user = User.objects.create_user(username='other', password='pass123')
        Transaction.objects.create(
            user=other_user, title='Other salary', amount=10000,
            type='income', date=datetime.date.today()
        )
        Transaction.objects.create(
            user=self.user, title='My salary', amount=50000,
            type='income', date=datetime.date.today()
        )
        response = self.client.get(reverse('transaction-list'))
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'My salary')


class SummaryTests(AuthTestCase):

    def setUp(self):
        super().setUp()
        Transaction.objects.create(
            user=self.user, title='Salary', amount=50000,
            type='income', date=datetime.date.today()
        )
        Transaction.objects.create(
            user=self.user, title='Rent', amount=15000,
            type='expense', date=datetime.date.today()
        )
        Transaction.objects.create(
            user=self.user, title='Groceries', amount=3000,
            type='expense', date=datetime.date.today()
        )

    def test_summary_totals(self):
        response = self.client.get(reverse('transaction-summary'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data['total_income']), 50000.0)
        self.assertEqual(float(response.data['total_expense']), 18000.0)
        self.assertEqual(float(response.data['balance']), 32000.0)

    def test_summary_empty(self):
        Transaction.objects.all().delete()
        response = self.client.get(reverse('transaction-summary'))
        self.assertEqual(float(response.data['total_income']), 0)
        self.assertEqual(float(response.data['total_expense']), 0)
        self.assertEqual(float(response.data['balance']), 0)
