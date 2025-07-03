
def get_info_needed(json):
    req = []

    # general-info
    if json['provider'] == 'not provided' or not json['subject']:
        req.append('general-info')

    # eligibility
    if 'not provided' in json['eligibility']['grades'] and list(json['eligibility']['age'].values()) == ['not provided', 'not provided']:
        req.append('eligibility')

    # dates
    if not any([deadline['name'] == 'Application Deadline' for deadline in json['deadlines']]):
        req.append('dates')

    # location
    if any([site['virtual'] == 'not provided' for site in json['locations']]):
        req.append('locations')
    
    # cost
    if any([plan['free'] == 'not provided' for plan in json['costs']]):
        req.append('costs')

    # contact
    if list(json['contact'].values()) == ['not provided', 'not provided']:
        req.append('contact')

    return req

"""import json
from pprint import pprint

with open('main/lib/schemas.json', 'r', encoding='utf-8') as file:
    schema = json.load(file)
    resp = schema['general-info'] | schema['eligibility'] | schema['dates'] | schema['locations'] | schema['costs'] | schema['contact']

pprint(resp)

print(get_info_needed(resp))"""