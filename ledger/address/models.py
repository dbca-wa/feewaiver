# from django.db import models
# from oscar.apps.address.abstract_models import AbstractUserAddress

# from oscar.apps.address.models import *  # noqa

from ledger.address.abstract_address_models import AbstractUserAddress

#if not is_model_registered('address', 'UserAddress'):
class UserAddress(AbstractUserAddress):
    pass

    class Meta:
         managed = False
         db_table = 'address_useraddress'
