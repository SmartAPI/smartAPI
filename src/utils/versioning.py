'''
Backup es index to S3 and refresh
'''

import logging

from tornado.ioloop import IOLoop

from web.api.es import ESQuery


def backup_and_refresh():
    '''
    Run periodically in the main event loop
    '''
    esq = ESQuery()
    try:
        esq.backup_all(aws_s3_bucket='smartapi')
    except:
        logging.exception("Backup failed.")
    try:
        esq.refresh_all(dryrun=False)
    except:
        logging.exception("Refresh failed.")


