
class Guards:
    @staticmethod
    def url_in_history(url, history, queue):
        if url in history:

            # URL already processed: remove from queue to avoid duplicate extraction
            removed_item = queue.pop(url)

            #self.logger.info(f"'{removed_item}' already in history, removing from queue...")
            return True
    
    @staticmethod
    def max_depth_reached(depth):
        if depth <= 0:

            #self.logger.info(f"Maximum depth recursion reached ({depth}), ending recursion...")
            return True
    
    @staticmethod
    def recieved_all_required_info(get_required_info, response):
        if not get_required_info(response):
            
            # All information already recieved, return to avoid unecessary extraction

            #self.logger.info(f"All required info recieved: ending recursion...")
            return True
        
    def guard_clauses(self, url, history, queue, depth, get_required_info, response):
        if self.url_in_history(url, history, queue):
            return True

        if self.max_depth_reached(depth):
            return True
    
        if self.recieved_all_required_info(get_required_info, response):
            return True