#!/usr/bin/env python3

from bs4 import BeautifulSoup
from requests import get
import re

class AwsSlaCrawler(object):
    
    def __init__(self):
        self.urls = [
            'https://aws.amazon.com/compute/sla/'
        ]
    
    def get_body(self, url):
        return(
            get(url).text
        )

    def soup_it(self, html):
        return(
            BeautifulSoup(html, 'html.parser')
        )

    def retrieve_updated_date(self, soup_data):
        return(
            soup_data.find(id=re.compile('^Last_Updated')).text
        )

    def sanitize_data(self, data):
        pass

    def compare_against_current_dataset(self, dynamo_backend, input_data):
        pass

    def update_data_set(self, dynamo_backend):
        pass

    def main(self):
        for url in self.urls:
            body = self.get_body(url=url)
            soup = self.soup_it(html=body)
            print(self.retrieve_updated_date(soup_data=soup))

if __name__ == '__main__':
    AwsSlaCrawler().main()