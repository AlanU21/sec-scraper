import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def scrape(cik):
    #Final list of soups
    result = []

    #Initialize driver
    base_url = "https://www.sec.gov/"
    landing_url = "edgar/browse/?CIK="
    options = webdriver.ChromeOptions
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)

    # Navigate to the URL and extract the name of the company
    url = base_url + landing_url + str(cik)
    driver.get(url)
    title = driver.find_element(By.ID, "name")
    name = title.text

    # Locate the expand button and open it
    h5_tags = driver.find_elements(By.TAG_NAME, "h5")
    for h5_tag in h5_tags:
        if h5_tag.text == "[+] 10-K (annual reports) and 10-Q (quarterly reports)":
            h5_tag.click()
            time.sleep(1)
            break

    # Locate the View All button and click it
    xpath = '//button[text()="View all 10-Ks and 10-Qs"]'
    button = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
    button.click()
    time.sleep(1)

    # Fetch the new page content and loop through the table to get all of the document urls
    document_urls = []
    table = driver.find_element(By.ID, 'filingsTable')
    rows = table.find_elements(By.TAG_NAME, 'tr')
    for row in rows[1:]:
        columns = row.find_elements(By.TAG_NAME, 'td')
        if len(columns) > 1:
            link_element = columns[1].find_element(By.TAG_NAME, 'a')
            if link_element:
                document_urls.append(link_element.get_attribute('href'))

    # Separate IXBRL documents and HTML documents
    ix_docs = []
    html_docs = []
    for url in document_urls:
        if url.__contains__('ix?'):
            ix_docs.append(url)
        else:
            html_docs.append(url)

    # For IXBRL documents, open them as HTML documents and then add soup contents to list
    for url in ix_docs:
        driver.get(url)
        # Locate and click the "Menu" dropdown
        menu_dropdown = wait.until(EC.element_to_be_clickable((By.ID, "menu-dropdown-link")))
        menu_dropdown.click()
        time.sleep(1)

        # Now, within the opened dropdown, locate the "Open as HTML" link and click it
        open_as_html_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Open as HTML')]")))
        open_as_html_link.click()
        time.sleep(1)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        result.append((soup, name))

    # For HTML documents, simply add soup contents to list
    for url in html_docs:
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        result.append((soup, name))

    driver.close()

    return result