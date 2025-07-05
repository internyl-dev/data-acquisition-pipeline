
def get_info_needed(json):
    req = []

    overview = json['overview']
    if overview['provider'] == 'not provided' or not overview['subject']:
        req.append('overview')

    eligibility = json['eligibility']
    if 'not provided' in eligibility['eligibility']['grades'] and list(eligibility['eligibility']['age'].values()) == ['not provided', 'not provided']:
        req.append('eligibility')

    dates = json['dates']
    if not any([deadline['name'] == 'Application Deadline' for deadline in dates['deadlines']]):
        req.append('dates')

    locations = json['locations']
    if any([site['virtual'] == 'not provided' for site in locations['locations']]):
        req.append('locations')
    
    costs = json['costs']
    if any([plan['free'] == 'not provided' for plan in costs['costs']]):
        req.append('costs')

    contact = json['contact']
    if list(contact['contact'].values()) == ['not provided', 'not provided']:
        req.append('contact')

    return req

"""import json
from pprint import pprint

with open('main/lib/schemas.json', 'r', encoding='utf-8') as file:
    schema = json.load(file)
    resp = schema['general-info'] | schema['eligibility'] | schema['dates'] | schema['locations'] | schema['costs'] | schema['contact']

pprint(resp)

print(get_info_needed(resp))"""