<!--[![Build
status](https://travis-ci.org/dbca-wa/disturbance.svg?branch=master)](https://travis-ci.org/dbca-wa/disturbance/builds) [![Coverage Status](https://coveralls.io/repos/github/dbca-wa/disturbance/badge.svg?branch=master)](https://coveralls.io/github/dbca-wa/disturbance?branch=master)-->
# Fee Waiver

The Fee Waiver System allows an unauthenticated user to apply for a park entry fee and/or camping fee waiver. It is a database-backed Django application, using REST API with Vue.js as the client side app.


# Requirements

- Python (3.8.x)
- PostgreSQL (>=9.3)

Python library requirements should be installed using `pip`:

`pip install -r requirements.txt`

# Environment settings

A `.env` file should be created in the project root and used to set
required environment variables at run time. Example content:

    DEBUG=True
    SECRET_KEY='thisismysecret'
    DATABASE_URL='postgis://USER:PASSWORD@HOST:PORT/DB_NAME'
    ALLOWED_HOSTS=[u'das.domain.com.au',u'das-internal.domain.com.au']
    EMAIL_HOST='EMAIL_HOST'
    BPOINT_MERCHANT_NUM='987654'
    BPAY_BILLER_CODE='121212'
    CMS_URL="https://url-used-to-retrieve-system-id-via-api/"
    OSCAR_SHOP_NAME='Shop 1'
    DEFAULT_FROM_EMAIL='system@email_address.com.au'
    NOTIFICATION_EMAIL='user.notification@email_address.com.au'
    NON_PROD_EMAIL='user_1@email_address.com.au,user_2@email_address.com.au'
    EMAIL_INSTANCE='DEV/TEST/UAT/PROD'
    PRODUCTION_EMAIL=False
    BPAY_ALLOWED=False
    LEDGER_GST=10
    SITE_PREFIX='das'
    SITE_DOMAIN='domain.com.au

