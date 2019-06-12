'''
Backup es index to S3 and refresh
'''

import logging

from tornado.ioloop import IOLoop

from web.api.es import ESQuery


async def backup_and_refresh():
    '''
    Run periodically in the main event loop
    '''
    def sync_func():
        esq = ESQuery()
        try:
            esq.backup_all(aws_s3_bucket='smartapi')
        except:
            logging.exception("Backup failed.")
        esq.refresh_all(dryrun=False)

    await IOLoop.current().run_in_executor(None, sync_func)
