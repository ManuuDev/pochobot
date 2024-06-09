import datetime
import json


class Exchange():
    def __init__(self, json_data):
        self.data = json.loads(json_data)
    
    def get_price(self, category, subcategory=None, key=None, property='price'):
        if subcategory and key:
            return self.data[category][subcategory][key][property]
        elif subcategory:
            return self.data[category][subcategory][property]
        else:
            return self.data[category][property]
    
    def get_variation(self, category, subcategory=None, key=None):
        if subcategory and key:
            return self.data[category][subcategory][key]['variation']
        elif subcategory:
            return self.data[category][subcategory]['variation']
        else:
            return self.data[category]['variation']
    
    def get_timestamp(self, category, subcategory=None, key=None):
        if subcategory and key:
            timestamp = self.data[category][subcategory][key]['timestamp']
        elif subcategory:
            timestamp = self.data[category][subcategory]['timestamp']
        else:
            timestamp = self.data[category]['timestamp']
        return datetime.fromtimestamp(timestamp)
