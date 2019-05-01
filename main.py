#!/usr/bin/env python3

from bs4 import BeautifulSoup
from requests import get
from src.dynamodb import DynamoDB
import re

# TODO: A lot of try/catch logic is missing here

class AwsSlaCrawler(object):
    
    def __init__(self, debug_mode=False):
        self.sla_main_page = 'https://aws.amazon.com/legal/service-level-agreements/'
        self.query_details = {"div": {"class": "aws-text-box section"}}
        self.debug_mode = debug_mode
        self.dynamo = DynamoDB(debug_mode=debug_mode)

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

    def convert_date_to_epoch(self, updated_date):
        from time import mktime, strptime
        updated_date = updated_date.replace('th', '')
        pattern = '%B %d, %Y'
        return(
            int(mktime(strptime(updated_date, pattern))) # This is nasty. Literally turning result into an int to avoid float, then back to a string. yay.
        )

    def debug_output(self, service_name, updated_date):
        print("{}: {}".format(
            service_name,
            updated_date
        ))

    def main(self):
        service_list = self.create_service_list()

        for url in service_list:

            body = self.get_body(url=url)
            soup = self.soup_it(html=body)
            service_name = url.split('/')[3]
            updated_date = self.retrieve_updated_date(soup_data=soup).replace(':','').split('Last Updated')[1].strip(' ') # Yuck, please don't judge me.
            epoch = self.convert_date_to_epoch(updated_date)

            if self.debug_mode:
                self.debug_output(service_name, updated_date)

            db_results = self.dynamo.query_db(service_name, updated_date)
            update_required = self.dynamo.compare_against_current_dataset(db_results=db_results, current_epoch=epoch)

            if update_required:
                self.dynamo.update_data_set(service_name, epoch)


if __name__ == '__main__':
    AwsSlaCrawler().main()