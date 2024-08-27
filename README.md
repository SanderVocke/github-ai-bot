Hello, world!

# github-ai-bot
A GitHub bot with AI-powered functionalities.

This bot is implemented as an Amazon AWS Lambda function to be ran in the cloud.

# Setup

- Run AWS Lambda docker container that this will run in in the cloud as well: e.g. `podman run -ti --entrypoint /bin/bash -v "$(pwd):/mnt/host" docker.io/amazon/aws-lambda-python:3.11`.
- Inside the container where you mounted the repo (`/mnt/host` above), run create_zips.py. This should generate two zip files in the root:
     - `function_pr_from_patch.zip` implements an endpoint function to create a pull request given a unified git diff.
     - `layer_github_ai_bot_lib.zip` is a Lambda Layer on which the endpoint lambda functions can run.

Some familiarity with AWS Lambda is required. The endpoint functions should be set up such that they use the library layer to work.

## Runtime

Both this layer and function are meant to run on the Pyhon 3.11 Lambda runtime.

## Environment variables

For endpoints, the following variables should be set:

- `GITHUB_APP_ID`: ID of your Github app.
- `GITHUB_PRIVATE_KEY`: App private key (PEM format). AWS cannot deal with newlines, so all newlines should be replaced by a literal "\n". `pem_key_to_env_var.py (file)` can help generate this.