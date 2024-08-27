from greptile_pr_bot.functions import submit_pr_from_patch
from greptile_pr_bot.exceptions import ResponseException

import logging
import json

logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    try:
        logging.basicConfig(level=logging.DEBUG)

        logger.debug(f"Event body: {event['body']}")

        body = json.loads(event['body'])

        # Extract details from the request body
        patch_content = body['patch_content']
        branch_name = body['branch_name'] if 'branch_name' in body else None
        user_email = body['user_email']
        description = body['description']
        repo_name = body['repo_name']
        base_branch = body['base_branch'] if 'base_branch' in body else None

        submit_pr_from_patch(
            repo_name,
            patch_content,
            user_email,
            description,
            branch_name,
            base_branch
        )

    except ResponseException as e:
        return {
            'statusCode': e.statusCode,
            'body': json.dumps({
                'message': e.errorMessage
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Internal server error:\n{str(e)}'
        }

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': f"Pull Request created"
        })
    }
