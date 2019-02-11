# Github Auditor

A repository which I intend to dump useful scripts which take advantage of the official Github API in order to improve/mandate security controls within a Github Organization.

Scripts are developed in Python 3.7 and are 'ready to deploy' using basic YAML templates.

## Scripts

### cron-github-auditor-2fa

This script is designed to enforce 2FA on Github member accounts within an Organization whilst maintaining a list of excluded accounts which for whatever reason, cannot be 2FA'd.
The script is triggered on a schedule/cron which calls the Github API for any members within your Organization that do not have 2FA enabled. Those that don't, get removed (unless they are in the exclusion list)

All output is sent to a Slack channel via a Webhook.

#### User Variables

  * `GITHUB_TOKEN` - A Personal Access Token (PAT) is required for the script to run - `admin:org` is the only permission required.
  * `SLACK_WEBHOOK` - provide a Slack incoming webhook so that the script can provide useful information to a channel of your choice
  * `ORGANIZATION` - provide the name of your Github Organization
  * `MAX_NUMBER_OF_USERS_TO_REMOVE` - this defines the maximum number of users that can be removed from an Organization in a single run. This is a safety measure in the event that the entire member set is returned from the API for whatever reason. Set this to a reasonable number that you don't expect to be removed from the organization.
  * `SAFE_MODE` - when this is set to True, the script will not remove any users if the number of users without 2FA is greater than the `MAX_NUMBER_OF_USERS_TO_REMOVE` variable
  * `TEST_MODE` - when this is set to True, the script will not remove any users, period. Use this when you're first starting out so you have a good idea of the number of users that will be removed when you're ready to set `TEST_MODE` to False.
  * `EXCLUDED_ACCOUNTS` - this is a Python list. Comma separated strings should be here - e.g., `['user-1', 'user-2']`


## Deploying

### AWS Lambda

The script has been designed to be deployed and run on AWS Lambda. You should be able to use something like the `serverless framework` to simply `serverless deploy` the script to your AWS account.

The script has been developed and tested on Python 3.7. It'll probably be fine on other versions but it's not something I have tested at this point in time.

### EC2/Physical/etc

The script can be easily modified so that it can be run anywhere other than AWS Lambda - I just haven't got around to making the modifications yet. If it's something you'd like to see then please raise an issue on Github and I'll get around to it!

## Screenshots

![Alt text](screenshots/normal-mode.png?raw=true "Script operating in normal operational mode")

![Alt text](screenshots/safe-mode.png?raw=true "Script operating in safe mode")

![Alt text](screenshots/test-mode.png?raw=true "Script operating in test/dry run mode")

![Alt text](screenshots/github-token-permissions.png?raw=true "Github personal access token permissions")
