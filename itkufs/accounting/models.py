from django.db import models
from django.contrib.auth.models import User
from django.utils.encoding import smart_unicode

class AccountGroup(models.Model):
    name = models.CharField(maxlength=100)
    slug = models.SlugField(prepopulate_from=['name'], unique=True,
        help_text='A shortname used in URLs etc.')
    warn_limit = models.IntegerField(null=True, blank=True)
    block_limit = models.IntegerField(null=True, blank=True)
    admins = models.ManyToManyField(User, null=True, blank=True)

    def __unicode__(self):
        return self.name

    def save(self):
        models.Model.save(self)
        # Create default accounts
        if not self.account_set.count():
            bank = Account(name='Bank', slug='bank', group=self, type='As')
            bank.save()
            cash = Account(name='Cash', slug='cash', group=self, type='As')
            cash.save()

    class Admin:
        pass

    class Meta:
        ordering = ['name']

class Account(models.Model):
    ACCOUNT_TYPE = [
        ('As', 'Asset'),     # Eiendeler/aktiva
        ('Li', 'Liability'), # Gjeld/passiva
        ('Eq', 'Equity'),    # Egenkapital
        ('In', 'Income'),    # Inntekt
        ('Ex', 'Expense'),   # Utgift
    ]

    name = models.CharField(maxlength=100)
    slug = models.SlugField(prepopulate_from=['name'],
        help_text='A shortname used in URLs etc.')
    group = models.ForeignKey(AccountGroup)
    type = models.CharField(maxlength=2, choices=ACCOUNT_TYPE, default='Li')
    owner = models.ForeignKey(User, null=True, blank=True)
    active = models.BooleanField(default=True)
    ignore_block_limit = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    def balance(self):
        """Returns account balance"""

        balance = 0

        for t in self.from_transactions.filter(payed__isnull=False):
            balance -= t.amount
        for t in self.to_transactions.filter(payed__isnull=False):
            balance += t.amount

        return balance

    def debit_to_increase(self):
        """Returns true if account type uses debit to increase, false if using
        credit to increase, and None for 'Equity' accounts, as those can do
        both."""

        if self.type in ('Li', 'In'):
            # Credit to increase
            return False
        elif self.type == 'Eq':
            # Depends on capital (credit/false) or drawing (debit/true)
            return None
        else:
            # Debit to increase
            return True

    def is_user_account(self):
        """Returns true if a user account"""

        if self.owner and self.type == 'Li':
            return True
        else:
            return False

    def is_blocked(self):
        """Returns true if user account balance is below group block limit"""

        if not self.is_user_account() or self.ignore_block_limit:
            return False
        return (-1 * self.balance()) < self.group.block_limit

    class Admin:
        fields = (
            (None,
                {'fields': ('name', 'slug', 'group', 'owner')}),
            ('Advanced options', {
                'classes': 'collapse',
                'fields' : ('type', 'active')}),
        )
        list_display = ['group', 'name', 'owner', 'balance', 'active']
        list_display_links = ['name']
        list_filter = ['active', 'group', 'name']
        list_per_page = 20
        search_fields = ['name']

    class Meta:
        ordering = ['group', 'name']
        unique_together = (('slug', 'group'),)

class Settlement(models.Model):
    date = models.DateField()

    def __unicode__(self):
        return smart_unicode(self.date)

    class Admin:
        pass

    class Meta:
        ordering = ['date']

class InvalidTransaction(Exception):
    def __init__(self, value):
        self.value = value

    def __unicode__(self):
        return u'Invalid transaction: %s' % self.value

class Transaction(models.Model):
    from_account = models.ForeignKey(Account,
                                     related_name='from_transactions')
    to_account = models.ForeignKey(Account,
                                   related_name='to_transactions')

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    details = models.CharField(maxlength=200, blank=True, null=True)

    registered = models.DateTimeField(auto_now_add=True)
    payed = models.DateTimeField(blank=True, null=True)

    settlement = models.ForeignKey(Settlement, null=True, blank=True)

    def __unicode__(self):
        return u'%s from %s to %s' % (self.amount,
                                      self.from_account,
                                      self.to_account)

    def save(self):
        if self.amount < 0:
            raise InvalidTransaction, 'Amount is negative.'

        if self.amount == 0:
            raise InvalidTransaction, 'Amount is zero.'

        if self.from_account == self.to_account:
            raise InvalidTransaction, 'Giving yourself money?'

        models.Model.save(self)

    class Admin:
        list_display = ['amount', 'from_account', 'to_account', 'settlement']
        list_filter = ['from_account', 'to_account', 'settlement']

    class Meta:
        ordering = ['registered', 'payed']

