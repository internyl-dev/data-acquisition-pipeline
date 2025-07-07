
def get_required_info(json):
    required_info = []

    overview = json['overview']
    if overview['provider'] == 'not provided' or not overview['subject']:
        required_info.append('overview')

    eligibility = json['eligibility']
    if 'not provided' in eligibility['eligibility']['grades'] and list(eligibility['eligibility']['age'].values()) == ['not provided', 'not provided']:
        required_info.append('eligibility')

    dates = json['dates']
    if any([deadline['date'] == 'not provided' for deadline in dates['deadlines']]):
        required_info.append('dates')

    locations = json['locations']
    if any([site['virtual'] == 'not provided' for site in locations['locations']]):
        required_info.append('locations')
    
    costs = json['costs']
    if any([plan['free'] == 'not provided' for plan in costs['costs']]):
        required_info.append('costs')

    contact = json['contact']
    if list(contact['contact'].values()) == ['not provided', 'not provided']:
        required_info.append('contact')

    return required_info

"""import json
from pprint import pprint

with open('main/lib/schemas.json', 'r', encoding='utf-8') as file:
    schema = json.load(file)
    resp = schema['general-info'] | schema['eligibility'] | schema['dates'] | schema['locations'] | schema['costs'] | schema['contact']

pprint(resp)

print(get_info_needed(resp))"""