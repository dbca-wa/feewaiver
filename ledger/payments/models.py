class OracleFinanceDBRouter(object):

    def db_for_read(self, model, **hints):
       if model._meta.db_table == 'payments_open_periods' or model._meta.db_table == 'payments_account_codes':
           return 'oracle_finance'
       return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write auth and contenttypes models go to auth_db.
        """
        return None