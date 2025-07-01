
def get_info_needed(json):
    req = []

    eligibility = json['eligibility']
    if eligibility['grades'] == 'not provided' and list(eligibility['age'].values()) == ['not provided', 'not provided']:
        req.append('eligibility')

    deadlines = json['deadlines']
    if not any([deadline['name'] == 'Application Deadline' for deadline in deadlines]):
        req.append('deadlines')
    
    cost = json['cost']
    if not cost:
        req.append('cost')
    
    return req
