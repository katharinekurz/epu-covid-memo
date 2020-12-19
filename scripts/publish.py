import os
import sys
import logging
import boto3
from pytz import timezone
from botocore.exceptions import ClientError
from datetime import datetime

ARTIFACT_NAME = 'headfile.xls'

S3_BUCKET = os.environ.get('S3_BUCKET')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_DEFAULT_REGION = os.environ.get('AWS_DEFAULT_REGION')

EST_TZ = timezone('US/Eastern')

TMPL_START = '<!-- tmpl start -->'
TMPL_END = '<!-- tmpl end -->'

def panic(msg):
    logging.error('Fatal: {}'.format(msg))
    sys.exit(1)


def get_expiry():
    '''
    Generate the expiry for the S3 object.
    Expiry will be the first day of the month, 2 months out.
    '''
    now = datetime.now(EST_TZ)
    year = now.year if not now.month >= 11 else now.year + 1
    month = (now.month + 2) % 12
    day = 1
    return datetime(year, month, day)


def get_artifact_name():
    now = datetime.now(EST_TZ)
    return "records/{}-{}-{}-{}{}{}-covid_artifact.xls".format(
        now.year, now.month, now.day, now.hour, now.minute, now.second
    )


def get_object_url(key):
    return "https://covid-artifacts.s3.amazonaws.com/{}".format(key)


def publish_artifact():
    '''
    Upload the excel file to the artifact bucket.
    It will be deleted on the first day of 
    '''
    client = boto3.resource('s3')
    key = get_artifact_name()
    expiry = get_expiry()

    try:
        fh = open(ARTIFACT_NAME, "rb")
    except Exception as e:
        logging.error(e)
        panic('failed to read file: {}'.format(ARTIFACT_NAME))

    try:
        client.Bucket(S3_BUCKET).put_object(
            ACL='public-read',
            Body=fh,
            Bucket=S3_BUCKET,
            Expires='2020-02-01',
            Key=key,
        )
        logging.info('successfully published artifact: {}'.format(key))
        url = get_object_url(key)
        return url
    except ClientError as e:
        logging.error(e)
        panic('failed to publish artifact')


def update_readme(url):
    now = datetime.now(EST_TZ)
    section = TMPL_START + """

## Dataset (last updated {})

Click [here]({}) to download.

""".format(now.strftime('%c'), url) + TMPL_END
    
    content = open('README.md', 'r').read()
    before = content.split(TMPL_START)[0]
    after = content.split(TMPL_END)[1]

    open('README.md', 'w').write(before + section + after)


if __name__ == '__main__':
    if not S3_BUCKET:
        panic('S3_BUCKET is required')
    if not AWS_SECRET_KEY:
        panic('AWS_SECRET_ACCESS_KEY is required')
    if not AWS_ACCESS_KEY:
        panic('AWS_ACCESS_KEY_ID is required')
    if not AWS_DEFAULT_REGION:
        panic('AWS_DEFAULT_REGION is required')
    
    url = publish_artifact()
    update_readme(url)
