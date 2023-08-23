from bs4 import BeautifulSoup
import pandas as pd
import processor
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

cik = 1803498

base_url = "https://www.sec.gov/"
landing_url = "edgar/browse/?CIK="
options = webdriver.ChromeOptions
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)


url = base_url + landing_url + str(cik)
driver.get(url)
title = driver.find_element(By.ID, "name")
name = title.text


h5_tags = driver.find_elements(By.TAG_NAME, "h5")
for h5_tag in h5_tags:
    if h5_tag.text == "[+] 10-K (annual reports) and 10-Q (quarterly reports)":
        h5_tag.click()
        time.sleep(1)
        break

xpath = '//button[text()="View all 10-Ks and 10-Qs"]'
button = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
button.click()
time.sleep(2)

html_content = driver.page_source

document_urls = []
table = driver.find_element(By.ID, 'filingsTable')
rows = table.find_elements(By.TAG_NAME, 'tr')
for row in rows[1:]:
    columns = row.find_elements(By.TAG_NAME, 'td')
    if len(columns) > 1:
        link_element = columns[1].find_element(By.TAG_NAME, 'a')
        if link_element:
            document_urls.append(link_element.get_attribute('href'))

ix_docs = []
html_docs = []
for url in document_urls:
    if url.__contains__('ix?'):
        ix_docs.append(url)
    else:
        html_docs.append(url)

for url in ix_docs:
    driver.get(url)
    # Locate and click the "Menu" dropdown
    menu_dropdown = wait.until(EC.element_to_be_clickable((By.ID, "menu-dropdown-link")))
    time.sleep(1)
    menu_dropdown.click()

    # Now, within the opened dropdown, locate the "Open as HTML" link and click it
    open_as_html_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Open as HTML')]")))
    open_as_html_link.click()
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    tables_with_phrase = []
    for table in soup.find_all('table'): 
        if ("consolidated schedule of investment" in table.get_text().lower()) and (name.lower() in table.get_text().lower()):
            # Find the div containing the phrase within the table
            div_containing_phrase = table.find('div', text=lambda x: "consolidated schedule of investment" in (x or '').lower())
            
            # If found, get the next div sibling which presumably contains the date
            if div_containing_phrase:
                next_div = div_containing_phrase.find_next_sibling('div')
                
                # Extract the text from that div (date_text can now be used for your Excel sheet name)
                date = next_div.get_text(strip=True) if next_div else None
                print(date)
            
            else:
                print("did not find")

            tables_with_phrase.append((table, date))
        break



    # for table in tables_with_phrase:
    #     processor.process(table, date)
    #     break

    break

#driver.close()