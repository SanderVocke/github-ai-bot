from github_ai_bot.functions import submit_pr_from_patch
from github_ai_bot.exceptions import ResponseException

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
        commit_msg = body['commit_msg'] if 'commit_msg' in body else 'commit'
        repo_name = body['repo_name']
        base_branch = body['base_branch'] if 'base_branch' in body else None

        pr_url = submit_pr_from_patch(
            repo_name = repo_name,
            patch_content = patch_content,
            user_email = user_email,
            description = description,
            branch_name = branch_name,
            base_branch_name = base_branch,
            commit_msg = commit_msg
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
