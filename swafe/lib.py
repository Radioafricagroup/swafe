import boto3
from botocore.client import Config


def init_swf():
    botoConfig = Config(connect_timeout=50, read_timeout=70)
    return boto3.client('swf', config=botoConfig)

swf = init_swf()
