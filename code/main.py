import scraper
import extract
import process
from bs4 import BeautifulSoup
import requests

# headers = {'user-agent': "alanuthuppan@yahoo.com"}

# response = requests.get("https://www.sec.gov/Archives/edgar/data/1803498/000180349823000012/bcred-20230331.htm", headers=headers)
# soup = BeautifulSoup(response.content, 'html.parser')

# Scrape the pages from the CIK 
cik = 1803498
filing_soups = scraper.scrape(cik)

# Extract all the relevant tables and dates from each filing
tables = []
for soup in filing_soups:
    tables.append(extract.extract(soup))

# Process each table into Excel format
for table in tables:
    process.process(table)