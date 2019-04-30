#!/usr/bin/env python3

from bs4 import BeautifulSoup
from requests import get
import re

class AwsSlaCrawler(object):
    
    def __init__(self):
        self.sla_main_page = 'https://aws.amazon.com/legal/service-level-agreements/'
        self.query_details = {"div": {"class": "aws-text-box section"}}
    
    def get_body(self, url):
        return(
            get(url).text
        )

    def soup_it(self, html):
        return(
            BeautifulSoup(html, 'html.parser')
        )

    def retrieve_updated_date(self, soup_data):
        """
        As expected, not all pages are the same. Some have different HTML formatting so if the id doesn't contain Last Updated, we try 'p' which seems to work
        """
        try:
            return(
                soup_data.find(id=re.compile('^Last_Updated')).text
            )
        except AttributeError:
            return(
                [x.getText() for x in soup_data.findAll('p') if 'Last Updated' in x.getText()][0]
            )
        else:
            print("SOMETHING WENT WRONG")

    def create_service_list(self):
        response = self.get_body(self.sla_main_page)
        soup = self.soup_it(response)
        element = list(self.query_details.keys())[0]
        values = self.query_details.get(element)
        sla_div = soup.findAll(element, values)[0]
        return(
            [url['href'] for url in sla_div.findAll('a', href=True)]
        )

    def compare_against_current_dataset(self, dynamo_backend, input_data):
        pass

    def update_data_set(self, dynamo_backend):
        pass

    def main(self):
        service_list = self.create_service_list()
        for url in service_list:
            body = self.get_body(url=url)
            soup = self.soup_it(html=body)
            service_name = url.split('/')[3]
            updated_date = self.retrieve_updated_date(soup_data=soup).replace(':','').split('Last Updated')[1].strip(' ')
            print("{}: {}".format(
                service_name,
                updated_date
            ))

if __name__ == '__main__':
    AwsSlaCrawler().main()