#!/usr/bin/env python3

from bs4 import BeautifulSoup
from requests import get
from dynamodb import DynamoDB
import re

# TODO: A lot of try/catch logic is missing here

class AwsSlaCrawler(object):
    
    def __init__(self, dynamo_table_name, debug_mode=False, local_mode=False):
        #self.sla_main_page = 'https://s3-us-west-2.amazonaws.com/sla-monitor-testing/sla_page.html' ## For Testing purposes
        self.sla_main_page = 'https://aws.amazon.com/legal/service-level-agreements/'
        self.query_details = {"div": {"class": "aws-text-box section"}}
        self.debug_mode = debug_mode
        self.local_mode = local_mode
        self.dynamo_table_name = dynamo_table_name
        self.dynamo = DynamoDB(dynamo_table=dynamo_table_name, debug_mode=debug_mode, local_mode=local_mode)

    def get_body(self, url):
        return(
            get(url).text
        )

    def soup_it(self, html):
        return(
            BeautifulSoup(html, 'html.parser')
        )

    def last_try(self, request_response, service_name):
        #[x.getText() for x in soup_data.findAll('p') if 'Last Updated' in x.getText()][0]
        try:
            updated_date = re.search(r'Last Updated(.*)', request_response)
            return updated_date[0]

        except Exception as e:
            # TODO: Add this to failed_service_update table so we can notify when we fail to properly scrape a service SLA page
            print("ERROR: After last try method, unable to parse website for {}. Please investigate. {}".format(service_name, e))
            pass

    def retrieve_updated_date(self, soup_data, request_response, service_name):
        """
        As expected, not all pages are the same. Some have different HTML formatting so if the id doesn't contain Last Updated, we try 'p' which seems to work
        """
        try:
            response = soup_data.find(id=re.compile('^Last_Updated')).text
            if not response:
                raise AttributeError
            return(response)
            #return(soup_data.body.findAll(text=re.compile('Last Updated(.*)$')))

        except AttributeError:
            print("HTML does not match the generic syntax for {}, moving on to last try method...".format(service_name))
            return self.last_try(request_response, service_name)

    def sanitize_date(self, date_string):
        date_string = date_string.replace(':','').replace('*','').split('Last Updated')[1].strip(' ') # Yuck, please don't judge me. This should be a regex.
        date_string = re.sub('<.*?>', "", date_string).strip()
        return date_string

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
            str(int(mktime(strptime(updated_date, pattern)))) # This is nasty. Literally turning result into an int to avoid float, then back to a string. yay.
        )

    def debug_output(self, service_name, updated_date):
        print("{}: {}".format(
            service_name,
            updated_date
        ))

    def main(self):
        service_list = self.create_service_list()

        for url in service_list:

            try:
                body = self.get_body(url=url)
                soup = self.soup_it(html=body)
                service_name = url.split('/')[3]
                pre_cleansed_date = self.retrieve_updated_date(soup_data=soup, request_response=body, service_name=service_name)
                #updated_date = pre_cleansed_date.replace(':','').replace('*','').split('Last Updated')[1].strip(' ') # Yuck, please don't judge me. This should be a regex.
                updated_date = self.sanitize_date(pre_cleansed_date)
                epoch = self.convert_date_to_epoch(updated_date)

                if self.debug_mode:
                    self.debug_output(service_name, updated_date)

                db_results = self.dynamo.query_db(service_name, updated_date)
                update_required = self.dynamo.compare_against_current_dataset(db_results=db_results, current_epoch=epoch)

                if update_required:
                    self.dynamo.update_data_set(service_name, epoch)

            except Exception as e:
                print("ERROR: MOVING ON, PLEASE REVIEW ERROR. {}".format(e))
                pass


if __name__ == '__main__':
    AwsSlaCrawler().main()