from ledger.address.abstract_country_models import AbstractCountry

class Country(AbstractCountry):
    pass

    class Meta:
       managed = False
       db_table = 'address_country'