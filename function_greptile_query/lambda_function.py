from github_ai_bot.functions import greptile_query
from github_ai_bot.exceptions import ResponseException
from github_ai_bot.logging import stream_and_level_for_all_loggers

import logging
import json

logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    try:
        stream_and_level_for_all_loggers(logging.DEBUG)

        logger.debug(f"Event body: {event['body']}")

        body = json.loads(event['body'])

        # Extract details from the request body
        message = body['message']
        branch_name = body['branch_name'] if 'branch_name' in body else None
        repo_name = body['repo_name']

        response = greptile_query(
            message = message,
            repo_name = repo_name,
            branch_name = branch_name
        )
        
        logger.debug(f"Response: {response.text}")
        
        return {
            'statusCode': response.status_code,
            'body': json.dumps(response.text)
        }

    except ResponseException as e:
        return {
            'statusCode': e.statusCode,
            'body': json.dumps({
                'message': e.errorMessage
            })
        }
