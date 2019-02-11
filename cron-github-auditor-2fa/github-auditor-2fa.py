from botocore.vendored import requests
import datetime

GITHUB_TOKEN = ''  # admin:org is the only permission required for this script to work
SLACK_WEBHOOK = ""
ORGANIZATION = ""  # The organization name in Github
# This is a fail-safe mechanism in the event that Github API screws up and returns unexpected results such
# as the entire org membership (that would be a bad, bad day). Set to a reasonable number of users you don't
# realistically expect to remove from the organization on a scheduled run.
MAX_NUMBER_USERS_TO_REMOVE = 3
SAFE_MODE = True  # When set to True, we will not remove members from the ORGANIZATION if > MAX_NUMBER_USERS_TO_REMOVE
TEST_MODE = True  # When set to True, we will not remove any members from the ORGANIZATION at all. Test dry-run.
# In a perfect world, this list would be empty. Add any accounts that absolutely cannot be 2FA'd here.
EXCLUDED_ACCOUNTS = []

DATE_TIME = datetime.datetime.now()
HEADERS = {'Authorization': 'token ' + GITHUB_TOKEN,
           'Accept': 'application/vnd.github.v3+json'}


def find_non_compliant_users(event, context):
    """
    This is the main function called by the script.

    First, a call is made to the Github API to retrieve all users in the organization with 2FA disabled. For every user
    in the organization, the user ID and profile URL is added to the non_compliant_users dictionary.

    If any non-compliant users were found, we send a Slack notification with the user ID and URL.

    Next we check whether the script is in TEST_MODE. If it is, we send a Slack notification saying so and do not
    continue to the removal stage.

    If the script is not in TEST_MODE, we check whether it is in SAFE_MODE. If it is, we continue to the removal stage
    but pass the MAX_NUMBER_USERS_TO_REMOVE parameter to the removal function.

    If neither TEST_MODE or SAFE_MODE is enabled, we go all out; big bang style.
    """
    
    non_compliant_users = dict()
    r = requests.get("https://api.github.com/orgs/" + ORGANIZATION + "/members?filter=2fa_disabled",
                     headers=HEADERS).json()
    for user in r:
        if user['login'] not in EXCLUDED_ACCOUNTS:
            non_compliant_users[user['login']] = user['html_url']
    if non_compliant_users:
        for user, url in non_compliant_users.items():
            notify_slack_channel(":x: Github - Non-compliant user found :x:", '#ff0000', user=user, url=url)
        if TEST_MODE:
            notify_slack_channel(":construction: Test mode is enabled. No users will be removed :construction:",
                                 '#FFFF00')
        elif SAFE_MODE:
            remove_non_compliant_users_from_organization(non_compliant_users,
                                                         MAX_NUMBER_USERS_TO_REMOVE=MAX_NUMBER_USERS_TO_REMOVE)
        else:
            remove_non_compliant_users_from_organization(non_compliant_users)


def remove_non_compliant_users_from_organization(users_to_remove, **kwargs):
    """
    This function removes non-compliant users from the organization and outputs the information to a Slack channel.

    First it checks whether the MAX_NUMBER_USERS_TO_REMOVE parameter has been passed through. If it has, we need to
    check whether there are more users to remove than the safety threshold. If the threshold has been hit, send a
    message to Slack and exit()

    If the safety threshold has not been hit, we can proceed to remove the users from the organization.
    """

    max_users_to_remove = kwargs.get('MAX_NUMBER_USERS_TO_REMOVE', None)
    if max_users_to_remove is not None and len(users_to_remove) > max_users_to_remove:
        notify_slack_channel(
            ":rotating_light: Github - Safety threshold (*" + str(max_users_to_remove) +
            "*) of users to remove from the organization has been hit.\n No users will be removed :rotating_light:",
            '#FFA500')
    else:
        for user, url in users_to_remove.items():
            try:
                r = requests.delete("https://api.github.com/orgs/" + ORGANIZATION + "/memberships/" + user,
                                    headers=HEADERS)
                if r.status_code == 204:
                    notify_slack_channel(
                        ":heavy_check_mark: Github - Non-compliant user was removed :heavy_check_mark:",
                        '#46A346', user=user, url=url)
            except Exception as e:
                notify_slack_channel("Error: " + str(e), '#ff0000')


def notify_slack_channel(message_type: str, colour: str, **kwargs):
    user_url = kwargs.get('url', None)
    user_id = kwargs.get('user', None)
    payload = {"attachments": [{
        "fallback": "Github Auditor - 2FA Alert",
        "pretext": message_type},
        {"title": "Date/Time ", "text": str(DATE_TIME), "color": colour},
        {"title": "User-ID: ", "text": user_id, "color": colour},
        {"title": "Profile URL: ", "text": user_url, "color": colour}
    ]}
    requests.post(SLACK_WEBHOOK, json=payload)
