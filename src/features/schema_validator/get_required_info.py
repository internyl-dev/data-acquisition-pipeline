
class RequiredInfo:
    def __init__(self):
        self.all_required_info = []

    def get_req_overview_info():
        pass

    def get_req_eligibility_infO():
        pass

    def get_req_dates_info():
        pass

    def get_req_locations_info():
        pass

    def get_req_costs_info():
        pass

    def get_req_contact_info():
        pass
    
    def get_required_info(self):
        required_info = []

        overview = self.response['overview']
        if overview['title'] == 'not provided':
            required_info.append('overview')

        eligibility = self.response['eligibility']
        if 'not provided' in eligibility['eligibility']['grades'] and list(eligibility['eligibility']['age'].values()) == ['not provided', 'not provided']:
            required_info.append('eligibility')

        dates = self.response['dates']
        if (
            any([deadline['date'] == 'not provided' and deadline['rolling_basis'] != True for deadline in dates['deadlines']]) or
            not any([deadline['priority'] == 'high' for deadline in dates['deadlines']])
            ):
            required_info.append('dates')

        locations = self.response['locations']
        if any([site['virtual'] == 'not provided' for site in locations['locations']]):
            required_info.append('locations')
        
        costs = self.response['costs']
        if any([plan['free'] == 'not provided' for plan in costs['costs']]):
            required_info.append('costs')

        contact = self.response['contact']
        if list(contact['contact'].values()) == ['not provided', 'not provided']:
            required_info.append('contact')

        return required_info

    def minimize_required_info(self, url, max_queue_length):
        if len(self.queue) > max_queue_length:

            # If the queue length is already really long, don't extract information that isn't needed
            # even if the information is specified as needed in the queue
            required_info = list(set(self.queue[url]) & set(self.get_required_info(self.response))) # Common required info between the two

            self.logger.info(f"High queue length ({max_queue_length}): minimizing information from {self.queue[url]} to {required_info}...\n")
            self.queue[url] = required_info