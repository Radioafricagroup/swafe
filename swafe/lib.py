import boto3
from botocore.client import Config


def init_swf():
    boto_config = Config(connect_timeout=50, read_timeout=70)
    return boto3.client('swf', config=boto_config)


swf = init_swf()
