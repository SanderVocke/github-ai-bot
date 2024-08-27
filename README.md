Hello, world!

# greptile-pr-bot
Greptile AI-based bot for automatically creating PRs.

This bot is implemented as an Amazon AWS Lambda function to be ran in the cloud.

# Setup

- Run AWS Lambda docker container that this will run in in the cloud as well: e.g. `podman run -ti --entrypoint /bin/bash -v "$(pwd):/mnt/host" docker.io/amazon/aws-lambda-python:3.11`.
- Inside the container where you mounted the repo (`/mnt/host` above), run create_zips.py. This should generate two zip files in the root:
     - `create-pr.zip` implements an endpoint function to create a pull request.
     - `python-dynamodb-pydeps.zip` is a Lambda Layer on which `create-pr` can run.

Some familiarity with AWS Lambda is required.

## Runtime

Both this layer and function are meant to run on the Pyhon 3.11 Lambda runtime.

## Environment variables

For `create-pr.zip`, the following variables should be set:

- `GITHUB_APP_ID`: ID of your Github app.
- `GITHUB_PRIVATE_KEY`: App private key (PEM format). AWS cannot deal with newlines, so all newlines should be replaced by a literal "\n". `pem_key_to_env_var.py (file)` can help generate this.