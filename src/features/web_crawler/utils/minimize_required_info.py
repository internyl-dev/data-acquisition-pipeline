
def minimize_required_info(url, queue, max_queue_length, all_required_info):
    if len(queue) > max_queue_length:

        # If the queue length is already really long, don't extract information that isn't needed
        # even if the information is specified as needed in the queue
        required_info = list(set(queue[url]) & set(all_required_info)) # Common required info between the two

        queue[url] = required_info