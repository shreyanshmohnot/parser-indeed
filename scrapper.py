"""
File Name: scrapper.py
Author: Shreyansh Mohnot
Desciption: indeed.com job description parser
usage: python scrapper.py ["job title/keyword"] [number of pages to crawl]
"""

import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import sys
import re

# job data storage variable
job_df = pd.DataFrame(columns=['Job Title', 'Company', 'Location', 'Description'])

# get job details from indeed url
# requries indeed job url as input
# returns job text description
def extract_job(url):
    job_page = bs(requests.get("http://indeed.com/viewjob?jk=" + url).text, "html.parser")
    return [descp.text.replace('\n', ' ').replace('\r', '') for descp in job_page.find_all(name="div", attrs={'class':'jobsearch-jobDescriptionText'})]

# gets the main web search page in HTML format from indeed.com, each page gives 10 job search
# requries attr - nums of pages to visit, info data, and location
# returns the HTML version of the web link pages
def main_search_page(num_pages, query, location):
    soups = []
    for i in range(num_pages):
        url = "https://www.indeed.com/jobs?q={0}&l={1}&sort=date&start={2}".format(query.replace(" ", "+"), location.replace(" ", "+"), i*10)
        page = requests.get(url)
        soup = bs(page.text, "html.parser")
        soups.append(soup)
    return soups


# def main function. Requires aguments from sys at command prompt.
# Stores data into dataframes.
def main(arg):
    
    num_pages = int(arg[1]) #10
    query = arg[0] #"tech"
    search_location = "United States"

    soups = main_search_page(num_pages, query, search_location)
    div_all = [soup.find_all('div', attrs={'class':'row'}) for soup in soups]
    
    for div in div_all:
        for d in div:
            job_detail = []
            if query.lower() in d.find('a', attrs={'class':'jobtitle'})['title'].lower():
                # get job title
                job_detail.append(d.find('a', attrs={'class':'jobtitle'})['title'])
                # get company name
                job_detail.append(d.find('span', attrs={'class':'company'}).text.strip())
                # get job location data
                job_detail.append(str.strip(re.sub('<[^<]+?>', '', str(d.find('span', attrs={'class':'company'})))))
                # get job description
                job_detail.append(extract_job(d['data-jk'])[0])
                # get job url
                # job_detail.append(div.a['href'])

                job_df.loc[d['data-jk']] = job_detail
    
    job_df.to_csv(query + ' jobs.csv')

# job_df.to_csv('indeed_jobs.csv', mode='a', header=False)

if __name__ == "__main__":
    main(sys.argv[1:])

