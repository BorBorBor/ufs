import unittest
from datetime import datetime

from itkufs.accounting.models import *
#import NewTransaction as Transaction # FIXME

# FIXME Write more tests
# FIXME Add docstrings explainging purpose of all tests

class GroupTestCase(unittest.TestCase):
    """Test the group model"""
    def setUp(self):
        pass

    def testDefaultGroup(self):
        pass

    def testPayedTransactionSet(self):
        """Check that payed_transaction_set only contains payed and related transactions"""
        # FIXME this test _will_ break when we change transaction model

        group = Group.objects.get(id=1)
        account1 = Account.objects.get(id=1)
        account2 = Account.objects.get(id=2)

        self.assertEqual(group.payed_transaction_set().count(), 0)

        # This one should show up
        t1 = Transaction(debit_account=account1, credit_account=account2,
            amount=100, payed=datetime.now())

        # Not payed show not be in set
        t2 = Transaction(debit_account=account1, credit_account=account2,
            amount=200)

        t1.save()
        t2.save()

        transactions = group.payed_transaction_set()
        for t in transactions:
            self.assert_(t.payed is not None)
            self.assertEqual(t.amount, 100)
            self.assert_(t.credit_account.group == group
                or t.debit_account.group == group)

        t1.delete()
        t2.delete()

    # ...

class AccountTestCase(unittest.TestCase):
    def setUp(self):
        self.group   = Group(name='Account Test Group', slug='account-test-group-slug')
        self.default = Account(name='Account Test', slug='account-test-slug')

    def testDefaultAccount(self):
        default = self.default

        self.assertEqual(default.name,'Account Test')
        self.assertEqual(default.ignore_block_limit, False)
        self.assertEqual(default.type, 'Li')
        self.assertEqual(default.owner, None)
        self.assertEqual(default.active, True)

    def testAccountTypes(self):
        pass

    def testAccountWithOwner(self):
        pass

    def testDisabledAccount(self):
        pass

    def testAccountBalance(self):
        pass

class TransactionlTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        # Remove all transactions...
        trans = Transaction.objects.all()
        for t in trans: t.delete()

    def testEmptyTransaction(self):
        """Check that transaction fails when no accounts are given"""
        pass

    def testNullAmountTransaction(self):
        """Check that transaction fail when debit and credit are not given"""
        pass

    def testDebitAndCreditAmmountEquall(self):
        """Check that transtion only accept sum(debit)==sum(credit)"""
        pass

    def testAccountOnlyInOneSideOfTransaction(self):
        """Check that debit accounts aren't present among credit accounts, and vica versa"""
        pass

    def testRegisteredLogEntry(self):
        """Check that a registered log entry is created"""
        pass

    def testPayedLogEntry(self):
        """Check creation of payed log entry"""
        pass

    def testRejectLogEntry(self):
        """Check that registered transaction can be rejected"""
        pass

    def testRejectPayedTransaction(self):
        """Test that rejecting payed transaction fails"""
        pass

    def testRejectRecievedTransaction(self):
        """Test that rejecting recieved transaction fails"""
        pass

    def testRecievePayedTransaction(self):
        """Check that we can set a payed transaction as recieved"""
        pass

    def testRecieveNotPayedTransaction(self):
        """Check that recieving a transaction that is not payed fails"""
        pass

    def testRejectRecievedTransaction(self):
        """Check that we can't reject a recieved transaction"""
        pass

    def testLogEntryUniqePerType(self):
        """Check that we can only have one log entry of each type"""
        pass

    def testLogEntryModify(self)
        """Test that modifying log entry raises error"""
        pass

    def testSimpleTransaction(self):
        """Baseline test to check transactions"""
        debit_account = Account.objects.get(id=1)
        credit_account = Account.objects.get(id=2)

        t = Transaction({'debit':100, 'account':debit_account},
            {'credit': 100, 'account':credit_account})

        entries = t.entry_set.all()
        debit = 0
        credit = 0
        for e in entries:
            if e.credit > 0:
                credit += e.credit
                self.assertEqual(credit_account, e.account)
            elif e.debit > 0:
                debit  += e.debit
                self.assertEqual(debit_account, e.account)
            else:
                self.fail('TransactionEntry with without valid credit or debit')

        self.assertEqual(credit, debit)

    def testTransActionWithManyDebitEntries(self):
        pass

    def testTransActionWithManyCreditEntries(self):
        pass

    def testTransactionLog(self):
        pass

    # ...
