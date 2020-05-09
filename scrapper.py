import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import sys

# job data storage variable
job_df = pd.DataFrame(columns=['Job Title', 'Company', 'Location', 'Description'])

# get job details from indeed url
# requries indeed job url as input
# returns job text description
def extract_job(url):
    job_page = bs(requests.get("http://indeed.com" + url).text, "html.parser")
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

def main(arg):
    
    num_pages = 99 #10
    query = arg[0] #"tech"
    search_location = "United States"

    soups = main_search_page(num_pages, query, search_location)
    
    for soup in soups:

        for div in soup.find_all(name='div', attrs={"class":"row"}):

            job_detail = []

            if "/rc/clk" in div.a['href'] and div.a['title'] in query:
                # get job title
                job_detail.append(div.a['title'])
                # get company name
                job_detail.append(div.span.text.strip())
                # get job location data
                job_detail.append(div.find(attrs={"location"}).text)
                # get job description
                job_detail.append(extract_job(div.a['href'])[0])
                # get job url
                # job_detail.append(div.a['href'])

                job_df.loc[div['data-jk']] = job_detail

    job_df.to_csv(query + ' jobs.csv')

# job_df.to_csv('indeed_jobs.csv', mode='a', header=False)

if __name__ == "__main__":
    main(sys.argv[1:])

