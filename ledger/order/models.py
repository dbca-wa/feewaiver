import json
from decimal import Decimal as D
from django.db import models
from ledger.accounts.models import Organisation
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import JSONField
# from oscar.apps.order.abstract_models import AbstractLine as CoreAbstractLine, AbstractOrder as CoreAbstractOrder

class Order(CoreAbstractOrder):

    organisation = models.ForeignKey(Organisation, null=True,blank=True, related_name='order_organisation')