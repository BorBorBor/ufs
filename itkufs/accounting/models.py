from django.db import models, transaction
from django.db.models import Q
from django.contrib import databrowse
from django.contrib.auth.models import User
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _
from django.core.validators import *

databrowse.site.register(User)

#FIXME replace custom save method with validator_lists where this can be done
#      and makes sense

class InvalidTransaction(Exception):
    def __init__(self, value):
        self.value = value

    def __unicode__(self):
        return u'Invalid transaction: %s' % self.value

class InvalidTransactionEntry(InvalidTransaction):
    def __unicode__(self):
        return u'Invalid transaction entry: %s' % self.value

class InvalidTransactionLog(InvalidTransaction):
    def __unicode__(self):
        return u'Invalid transaction log: %s' % self.value

class Group(models.Model):
    name = models.CharField(_('name'), max_length=100)
    slug = models.SlugField(_('slug'), prepopulate_from=['name'], unique=True,
        help_text=_('A shortname used in URLs etc.'))
    warn_limit = models.IntegerField(_('warn limit'), null=True, blank=True)
    block_limit = models.IntegerField(_('block limit'), null=True, blank=True)
    admins = models.ManyToManyField(User, verbose_name=_('admins'),
        null=True, blank=True)
    bank_account = models.ForeignKey('Account', verbose_name=_('bank account'),
        null=True, blank=True, related_name='foo', editable=False)
    cash_account = models.ForeignKey('Account', verbose_name=_('cash account'),
        null=True, blank=True, related_name='bar', editable=False)
    # FIXME: Fix related name of *_account
    # FIXME: Probably needs to add sales_account etc.

    logo = models.ImageField(upload_to='logos', null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = _('group')
        verbose_name_plural = _('groups')

    class Admin:
        pass

    def __unicode__(self):
        return self.name

    def save(self):
        super(Group, self).save()
        # Create default accounts
        if not self.account_set.count():
            # FIXME _('Bank') and _('Cash') does not seem to work here...
            # Could the problem be related to lazy/non-lazy ugettext?
            bank = Account(name='Bank', slug='bank', type='As', group=self)
            bank.save()
            cash = Account(name='Cash', slug='cash', type='As', group=self)
            cash.save()

            self.bank_account = bank;
            self.cash_account = cash;
            super(Group, self).save()

    # FIXME Use property for all elements?
    def get_user_account_set(self):
        """Returns queryset of user accounts"""
        return self.account_set.filter(type='Li', owner__isnull=False)
    user_account_set = property(get_user_account_set,None,None)

    def group_account_set(self):
        """Returns array of group accounts"""
        return self.account_set.exclude(type='Li', owner__isnull=False)

    def transaction_set_with_rejected(self):
        """Returns all transactions connected to group, including rejected"""
        return Transaction.objects.filter(
            entry_set__account__group=self).distinct()

    def transaction_set(self):
        """Returns all transactions connected to group, that have not been
        rejected"""
        return self.transaction_set_with_rejected().exclude(log_set__type='Rej')

    def registered_transaction_set(self):
        """Returns all transactions connected to group, that are not rejected"""
        return self.transaction_set().filter(log_set__type='Reg')

    def payed_transaction_set(self):
        """Returns all payed transactions connected to group, that are not
        rejected"""
        return self.transaction_set().filter(log_set__type='Pay')

    def not_payed_transaction_set(self):
        """Returns all unpayed transactions connected to group, that are not
        rejected"""
        return self.transaction_set().exclude(log_set__type='Pay')

    def received_transaction_set(self):
        """Returns all received transactions connected to group"""
        return self.transaction_set().filter(log_set__type='Rec')

    def not_received_transaction_set(self):
        """Returns all transactions that have not been received connected to
        group"""
        return self.transaction_set().exclude(log_set__type='Rec')

    def rejected_transaction_set(self):
        """Returns all rejected transactions connected to group"""
        return self.transaction_set().filter(log_set__type='Rej')

    not_rejected_transaction_set = transaction_set
    not_rejected_transaction_set.__doc__ = """Returns all transactions that
    have not been rejected connected to group. Same as transaction_set()."""
databrowse.site.register(Group)

ACCOUNT_TYPE = (
    ('As', _('Asset')),     # Eiendeler/aktiva
    ('Li', _('Liability')), # Gjeld/passiva
    ('Eq', _('Equity')),    # Egenkapital
    ('In', _('Income')),    # Inntekt
    ('Ex', _('Expense')),   # Utgift
)

class Account(models.Model):
    name = models.CharField(_('name'), max_length=100)
    slug = models.SlugField(_('slug'), prepopulate_from=['name'],
        help_text=_('A shortname used in URLs etc.'))
    group = models.ForeignKey(Group, verbose_name=_('group'))
    type = models.CharField(_('type'), max_length=2, choices=ACCOUNT_TYPE,
        default='Li')
    owner = models.ForeignKey(User, verbose_name=_('owner'),
        null=True, blank=True)
    active = models.BooleanField(_('active'), default=True)
    ignore_block_limit = models.BooleanField(_('ignore block limit'),
        default=False)

    class Meta:
        ordering = ['group', 'type', 'name']
        unique_together = (('slug', 'group'),)
        verbose_name = _('account')
        verbose_name_plural = _('accounts')

    class Admin:
        fields = (
            (None,
                {'fields': ('name', 'slug', 'group', 'owner')}),
            (_('Advanced options'), {
                'classes': 'collapse',
                'fields' : ('type', 'active', 'ignore_block_limit')}),
        )
        list_display = ['group', 'name', 'type', 'owner', 'balance',
            'active', 'ignore_block_limit']
        list_display_links = ['name']
        list_filter = ['active', 'type', 'group']
        list_per_page = 20
        search_fields = ['name']

    def __unicode__(self):
        return "%s: %s" % (self.group, self.name)

    def debit_to_increase(self):
        """Returns True if account type uses debit to increase, False if using
        credit to increase, and None for all equity accounts."""

        if self.type in ('Li', 'In'):
            # Credit to increase
            return False
        elif self.type in ('As', 'Ex'):
            # Debit to increase
            return True
        else:
            # Equity accounts: Credit to increase for capital accounts, debit
            # to increase of drawing accounts
            return None

    def balance(self):
        """Returns account balance"""

        balance = 0

        for e in self.transactionentry_set.filter(transaction__log_set__type='Rec'):
            balance -= e.debit
            balance += e.credit

        return balance

    def balance_credit_reversed(self):
        """Returns account balance. If the account is an credit account, the
        balance is multiplied with -1."""

        balance = self.balance()
        if balance == 0 or self.debit_to_increase():
            return balance
        else:
            return -1 * balance

    def is_user_account(self):
        """Returns true if a user account"""

        if self.owner is not None and self.type == 'Li':
            return True
        else:
            return False

    def is_blocked(self):
        """Returns true if user account balance is below group block limit"""

        if (not self.is_user_account()
            or self.ignore_block_limit
            or self.group.block_limit is None):
            return False
        return self.balance_credit_reversed() < self.group.block_limit

    def needs_warning(self):
        """Returns true if user account balance is below group warn limit"""

        if (not self.is_user_account()
            or self.ignore_block_limit
            or self.group.warn_limit is None):
            return False
        return self.balance_credit_reversed() < self.group.warn_limit
databrowse.site.register(Account)

class Settlement(models.Model):
    date = models.DateField(_('date'))
    comment = models.CharField(_('comment'), max_length=200,
        blank=True, null=True)

    class Meta:
        ordering = ['date']
        verbose_name = _('settlement')
        verbose_name_plural = _('settlements')

    class Admin:
        pass

    def __unicode__(self):
        if self.comment is not None:
            return smart_unicode("%s: %s" % (self.date, self.comment))
        else:
            return smart_unicode(self.date)
databrowse.site.register(Settlement)

class Transaction(models.Model):
    settlement = models.ForeignKey(Settlement, verbose_name=_('settlement'),
        null=True, blank=True)
    user = None # Not a django field as we use this for a hack
    message = ''

    class Meta:
        verbose_name = _('transaction')
        verbose_name_plural = _('transactions')

    #class Admin:
    #    pass

    def __unicode__(self):
        if self.entry_set.all().count():
            return ','.join([str(entry) for entry in self.entry_set.all()])
        else:
            return u'Empty transaction'

    def debug(self):
        status = self.log_set.all()
        return "%s %s" % (self.__unicode__(), status)

    @transaction.commit_manually # TODO check how the state is code fails...
    def save(self):
        try:
           debit_sum = 0
           credit_sum = 0

           for entry in self.entry_set.all():
               debit_sum += float(entry.debit)
               credit_sum += float(entry.credit)

           if debit_sum != credit_sum:
               raise InvalidTransaction(_('Credit and debit do not match'))

           super(Transaction, self).save()

        except InvalidTransaction, e:
            transaction.rollback()
            raise e
        else:
            transaction.commit()

    def set_registered(self, user=None, message=''):
        self.save()

        if self.id is None:
            self.save()

        if not self.is_registered():
            log = TransactionLog(type='Reg', transaction=self)
            if user:
                log.user = user
            if message is not None and message.strip() != '':
                log.message = message
            log.save()
        else:
            raise InvalidTransaction(_('Could not set transaction as registered'))

    def set_payed(self, user=None, message=''):
        if not self.is_rejected() and self.is_registered():
            log = TransactionLog(type='Pay', transaction=self)
            if user:
                log.user = user
            if message.strip() != '':
                log.message = message
            log.save()
        else:
            raise InvalidTransaction(_('Could not set transaction as payed'))

    def set_received(self, user=None, message=''):
        if not self.is_rejected() and self.is_registered() and self.is_payed():
            log = TransactionLog(type='Rec', transaction=self)
            if user:
                log.user = user
            if message.strip() != '':
                log.message = message
            log.save()
        else:
            raise InvalidTransaction(_('Could not set transaction as received'))

    def reject(self, user=None, message=''):
        if self.is_registered() and not self.is_payed() and not self.is_received():
            log = TransactionLog(type='Rej', transaction=self)
            if user:
                log.user = user
            if message.strip() != '':
                log.message = message
            log.save()
        else:
            raise InvalidTransaction(_('Could not set transaction as rejected'))
    set_rejected = reject
    set_rejected.__doc__ = 'set_rejected() is an alias for reject()'

    def is_registered(self):
        return self.log_set.filter(type='Reg').count() > 0

    def is_payed(self):
        return self.log_set.filter(type='Pay').count() > 0

    def is_received(self):
        return self.log_set.filter(type='Rec').count() > 0

    def is_rejected(self):
        return self.log_set.filter(type='Rej').count() > 0

    def get_registered(self):
        if self.is_registered():
            return self.log_set.filter(type='Reg')[0];
    def get_payed(self):
        if self.is_payed():
            return self.log_set.filter(type='Pay')[0];
    def get_received(self):
        if self.is_received():
            return self.log_set.filter(type='Rec')[0];
    def get_rejected(self):
        if self.is_rejected():
            return self.log_set.filter(type='Rej')[0];

    registered = property(get_registered, None, None)
    received = property(get_received, None, None)
    rejected = property(get_rejected, None, None)
    payed = property(get_payed, None, None)

    class Admin:
        pass
databrowse.site.register(Transaction)

TRANSACTIONLOG_TYPE = (
    ('Reg', _('Registered')),
    ('Pay', _('Payed')),
    ('Rec', _('Received')),
    ('Rej', _('Rejected')),
)

class TransactionLog(models.Model):
    transaction = models.ForeignKey(Transaction,
        verbose_name=_('transaction'), related_name='log_set',
        edit_inline=models.TABULAR, num_in_admin=3, max_num_in_admin=4,
        num_extra_on_change=1)
    type = models.CharField(_('type'), max_length=3, core=True,
        choices=TRANSACTIONLOG_TYPE)
    timestamp =  models.DateTimeField(_('timestamp'), auto_now_add=True)
    user = models.ForeignKey(User, verbose_name=_('user'))
    message = models.CharField(_('message'), max_length=200, blank=True)

    def save(self):
        if self.id is not None:
            raise InvalidTransactionLog(
                _('Altering transaction log entries is not allowed'))
        if self.transaction.id is None:
            self.transaction.save()
        super(TransactionLog, self).save()

    class Meta:
        unique_together = (('transaction', 'type'),)
        verbose_name = _('transaction log entry')
        verbose_name_plural = _('transaction log entries')

    def __unicode__(self):
        return _(u'%(type)s at %(timestamp)s by %(user)s: %(message)s') % {
            'type': self.get_type_display(),
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M'),
            'user': self.user,
            'message': self.message,
        }
databrowse.site.register(TransactionLog)

class TransactionEntry(models.Model):
    transaction = models.ForeignKey(Transaction,
        verbose_name=_('transaction'), related_name='entry_set',
        edit_inline=models.TABULAR, num_in_admin=5, num_extra_on_change=3)
    account = models.ForeignKey(Account, verbose_name=_('account'), core=True)
    debit = models.DecimalField(_('debit amount'),
        max_digits=10, decimal_places=2, default=0)
    credit = models.DecimalField(_('credit amount'),
        max_digits=10, decimal_places=2, default=0)

    def save(self):
        if self.transaction.is_registered():
            raise InvalidTransactionEntry(
                _("Can't add entries to registered transactions"))

        if self.debit < 0 or self.credit < 0:
            raise InvalidTransactionEntry(
                _('Credit and debit must be positive or zero'))

        if self.debit > 0 and self.credit > 0:
            raise InvalidTransactionEntry(
                _('Only credit or debit may be set'))

        if self.debit == 0 and self.credit == 0:
            raise InvalidTransactionEntry(
                _('Create or debit must be positive'))

        super(TransactionEntry, self).save()

    class Meta:
        unique_together = (('transaction', 'account'),)
        verbose_name = _('transaction entry')
        verbose_name_plural = _('transaction entries')

    def __unicode__(self):
        return _(u'%(account)s: debit %(debit)s, credit %(credit)s') % {
            'account': self.account,
            'debit': self.debit,
            'credit': self.credit,
        }
databrowse.site.register(TransactionEntry)
