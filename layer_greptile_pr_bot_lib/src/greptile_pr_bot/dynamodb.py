import boto3
from .environment_settings import DYNAMODB_TABLE

table = None

def init():
    global table
    if table == None:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(DYNAMODB_TABLE)