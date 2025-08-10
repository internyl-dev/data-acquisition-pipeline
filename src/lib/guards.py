
class Guards:

    def url_in_history(self, url):
        if url in self.history:

            # URL already processed: remove from queue to avoid duplicate extraction
            removed_item = self.queue.pop(url)

            self.logger.debug(f"'{removed_item}' already in history, removing from queue...")
            return True

    def max_depth_reached(self, depth):
        if depth <= 0:

            self.logger.debug(f"Maximum depth recursion reached ({depth}), ending recursion...")
            return True

    def recieved_all_required_info(self):
        if not self.get_required_info():
            
            # All information already recieved, return to avoid unecessary extraction

            self.logger.debug(f"All required info recieved: ending recursion...")
            return True
        
    def guard_clauses_main(self, url, depth):
        if self.url_in_history(url):
            return True

        if self.max_depth_reached(depth):
            return True
    
        if self.recieved_all_required_info():
            return True