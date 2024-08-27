import os

GITHUB_APP_ID = os.getenv('GITHUB_APP_ID')
GITHUB_PRIVATE_KEY = os.getenv('GITHUB_PRIVATE_KEY').strip().replace('\\n', '\n')
DYNAMODB_TABLE = os.getenv('DYNAMODB_TABLE')