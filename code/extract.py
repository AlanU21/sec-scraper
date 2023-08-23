from bs4 import BeautifulSoup

def extract(soup, name):
    # List to store the result (tuples of table and date)
    result = []

    # Search for div containing "Consolidated Schedule of Investments"
    for table in soup.find_all('table'): 
        if ("consolidated schedule of investment" in table.get_text().lower()) and (name.lower() in table.get_text().lower()):
            
            # Find the div/span containing the phrase within the table
            element_containing_phrase = table.find(lambda tag: tag.name in ["div", "span"] and "consolidated schedule of investment" in (tag.get_text() or '').lower())

            # If found and it's a div, get the next div sibling
            if element_containing_phrase and element_containing_phrase.name == 'div':
                next_div = element_containing_phrase.find_next_sibling('div')
                if next_div:
                    date_text = next_div.get_text()
                    result.append((table, date_text.strip()))
            
            # If found and it's a span, split on br tags to get list of strings
            elif element_containing_phrase and element_containing_phrase.name == 'span':
                texts = element_containing_phrase.stripped_strings
                texts_list = list(texts)
                date_text = texts_list[texts_list.index("Consolidated Schedule of Investments") + 1] if "Consolidated Schedule of Investments" in texts_list else None
                if date_text:
                    result.append((table, date_text.strip()))

    return result