
import re

class URLRanker:
    def weight_urls_keywords(self, response:dict, all_links:dict):
        weighed_queue = {}

        # Split title based on the delimitters ' ' and '-'
        title_keywords = re.split(' |-', response['overview']['title'])

        matches = 0
        for link in all_links:

            for title_keyword in title_keywords:
                if re.search(fr'{title_keyword}', link, re.I):
                    matches += 1
                if re.search(fr'{title_keyword}', all_links[link], re.I):
                    matches += 1
            
            if not weighed_queue:
                weighed_queue[link] = (all_links[link], matches)
            else:
                for key in weighed_queue:
                    if matches < weighed_queue[key][1]:
                        continue
                    items = list(weighed_queue.items())
                    position = list(weighed_queue.keys()).index(key)
                    items.insert(position, (link, (all_links[link], matches)))
                    weighed_queue = dict(items)
                    break
            
            matches = 0
        
        return weighed_queue
    
    def weigh_links_url(self, all_links:dict):
        pass