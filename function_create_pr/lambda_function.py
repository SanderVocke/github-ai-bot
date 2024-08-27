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

        pr_url = submit_pr_from_patch(
            repo_name,
            patch_content.encode('utf-8'),
            user_email,
            description,
            branch_name,
            base_branch
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f"Pull Request created @ {pr_url}"
            })
        }

    except ResponseException as e:
        return {
            'statusCode': e.statusCode,
            'body': json.dumps({
                'message': e.errorMessage
            })
        }
