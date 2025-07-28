from collections import defaultdict
import pandas as pd

def update_data_with_corpus_app(aidev, techlead, users):
    phone_set = build_user_phone_set(users)

    aidev_updated = []
    for row in aidev:
        mobile_no = row.get('Contact Number')
        mobile_no = normalize_number(mobile_no)
        row['corpus_app'] = 'done' if mobile_no in phone_set else ''
        aidev_updated.append(row)

    techlead_updated = []
    for row in techlead:
        mobile_no = row.get('Contact Number')
        mobile_no = normalize_number(mobile_no)
        row['corpus_app'] = 'done' if mobile_no in phone_set else ''
        techlead_updated.append(row)

    return aidev_updated, techlead_updated

def normalize_number(number):
    if not number:
        return None
    number = number.strip().replace(' ', '').replace('-', '')
    if number.startswith('+91'):
        return number
    if number.startswith('0'):
        number = '+91'+number[1:]
    if not number.startswith('+91'):
        number = '+91' + number
    return number

def build_user_phone_set(users):
    return set(user.get('phone') for user in users if user.get('phone'))

# def update_users_with_gitlabinfo(gitlab_users, aidev_data, techlead_data):
#     gitlab_emails = {
#         user['email'].strip().lower()
#         for user in gitlab_users
#         if isinstance(user, dict) and user.get('email')
#     }
#     aidev_data = pd.DataFrame(aidev_data)
#     techlead_data = pd.DataFrame(techlead_data)

#     aidev_data['has_gitlab_account'] = aidev_data['Email Address'].str.strip().str.lower().isin(gitlab_emails).map({True: 'Yes', False: 'No'})
#     techlead_data['has_gitlab_account'] = techlead_data['Email Address'].str.strip().str.lower().isin(gitlab_emails).map({True: 'Yes', False: 'No'})

#     return aidev_data.to_dict(orient='records'), techlead_data.to_dict(orient='records')

def update_users_with_gitlabinfo(gitlab_users, aidev_data, techlead_data):
  
  email_to_username = {
    user['email'].strip().lower(): user.get('username')
    for user in gitlab_users
    if isinstance(user, dict) and user.get('email') and user.get('username')
  }

  gitlab_emails = set(email_to_username.keys())

  aidev_data = pd.DataFrame(aidev_data)
  techlead_data = pd.DataFrame(techlead_data)

  for df in [aidev_data, techlead_data]:
    email_series = df['Email Address'].str.strip().str.lower()
    df['has_gitlab_account'] = email_series.isin(gitlab_emails).map({True: 'Yes', False: 'No'})
    df['gitlab_username'] = email_series.map(email_to_username)

  return aidev_data.to_dict(orient='records'), techlead_data.to_dict(orient='records')

def aggregate_data_collegewise(aidev_updated, techlead_updated, analytics_type):
    summary = defaultdict(lambda: {
        'total_registrations': 0,
        'no_of_accounts_created': 0,
        'no_of_accounts_needed': 0
    })

    for row in aidev_updated:
        affiliation = row['Affiliation (College/Company/Organization Name)'].strip()

        if analytics_type == "gitlab_analytics":
            account_status = row['has_gitlab_account'].strip().lower()
            summary[affiliation]['total_registrations'] += 1
            if account_status == 'yes':
                summary[affiliation]['no_of_accounts_created'] += 1
            else:
                summary[affiliation]['no_of_accounts_needed'] += 1
        else:
            account_status = row['corpus_app'].strip().lower()
            summary[affiliation]['total_registrations'] += 1
            if account_status == 'done':
                summary[affiliation]['no_of_accounts_created'] += 1
            else:
                summary[affiliation]['no_of_accounts_needed'] += 1

    aidev_collegewise_gitlab = [
        {
            'Affiliation': affiliation,
            'total_registrations': counts['total_registrations'],
            'no_of_accounts_created': counts['no_of_accounts_created'],
            'no_of_accounts_needed': counts['no_of_accounts_needed']
        }
        for affiliation, counts in summary.items()
    ]

    summary = defaultdict(lambda: {
        'total_registrations': 0,
        'no_of_accounts_created': 0,
        'no_of_accounts_needed': 0
    })

    for row in techlead_updated:
        affiliation = row['Affiliation (College/Company/Organization Name)'].strip()
        if analytics_type == "gitlab_analytics":
            account_status = row['has_gitlab_account'].strip().lower()
            summary[affiliation]['total_registrations'] += 1
            if account_status == 'yes':
                summary[affiliation]['no_of_accounts_created'] += 1
            else:
                summary[affiliation]['no_of_accounts_needed'] += 1
        else:
            account_status = row['corpus_app'].strip().lower()
            summary[affiliation]['total_registrations'] += 1
            if account_status == 'done':
                summary[affiliation]['no_of_accounts_created'] += 1
            else:
                summary[affiliation]['no_of_accounts_needed'] += 1

    tl_collegewise_gitlab = [
        {
            'Affiliation': affiliation,
            'total_registrations': counts['total_registrations'],
            'no_of_accounts_created': counts['no_of_accounts_created'],
            'no_of_accounts_needed': counts['no_of_accounts_needed']
        }
        for affiliation, counts in summary.items()
    ]
    return aidev_collegewise_gitlab, tl_collegewise_gitlab


def filter_no_gitlab_accounts(data_updated):
    df = pd.DataFrame(data_updated)

    # Filter rows where has_gitlab_account is 'no'
    filtered_df = df[df['has_gitlab_account'].str.strip().str.lower() == 'no']

    # Convert back to a list of dicts
    account_creation = filtered_df.to_dict(orient='records')

    return account_creation

def filter_no_corpus_accounts(data_updated):
    df = pd.DataFrame(data_updated)

    # Filter rows where has_gitlab_account is 'no'
    filtered_df = df[df['corpus_app'].str.strip().str.lower() == '']

    # Convert back to a list of dicts
    account_creation = filtered_df.to_dict(orient='records')

    return account_creation

