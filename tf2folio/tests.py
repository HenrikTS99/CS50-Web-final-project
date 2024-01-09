from django.test import TestCase, Client
from .models import User, Item, Transaction, Value
import datetime
# Create your tests here.


class ViewTestCase(TestCase):
    def setUp(self):
        # Create user
        self.user = User.objects.create_user(username='testuser', password='12345')
        # Create item
        self.item = Item.objects.create(item_name='Test Item', owner=self.user)

        # Create transaction
        self.transaction = Transaction.objects.create(owner=self.user)
        self.transaction.items_sold.set([self.item])

        # Create client
        self.client = Client()

    def test_index_view(self):
        self.client.login(username='testuser', password='12345')

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

        # Check that the context contains the user's items
        self.assertEqual(response.context['items'][0], self.item)

    def test_trade_history_view(self):
        self.client.login(username='testuser', password='12345')

        # Get the trade history view
        response = self.client.get('/trade_history')

        # Check that the response has a status code of 200
        self.assertEqual(response.status_code, 200)

        # Check that the context contains the user's transactions
        self.assertEqual(response.context['all_trades'][0], self.transaction)


class TransactionTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.item1 = Item.objects.create(item_name='Item 1', owner=self.user)
        self.item2 = Item.objects.create(item_name='Item 2', owner=self.user)

    def test_create_transaction(self):

        transaction_keys = Transaction.objects.create(
            owner=self.user,
            transaction_type='sale',
            description='Test transaction keys method',
            date = datetime.datetime.now()
        )

        transaction_value = Value.objects.create(
            transaction=transaction_keys, 
            transaction_method='keys', 
            amount=100
            )
        transaction_keys.transaction_value = transaction_value
        transaction_keys.save()

        # Add items to the transaction
        transaction_keys.items_sold.add(self.item1)
        transaction_keys.items_bought.add(self.item2)

        # Check that the transaction was created correctly
        self.assertEqual(transaction_keys.owner, self.user)
        self.assertEqual(transaction_keys.transaction_type, 'sale')
        self.assertEqual(transaction_keys.transaction_method, 'keys')
        self.assertEqual(transaction_keys.currency, None)
        self.assertEqual(transaction_keys.amount, 100)
        self.assertEqual(transaction_keys.description, 'Test transaction keys method')
        self.assertIn(self.item1, transaction_keys.items_sold.all())
        self.assertIn(self.item2, transaction_keys.items_bought.all())