import pandas as pd
import requests
from bs4 import BeautifulSoup
from openpyxl import load_workbook
from openpyxl.styles import Alignment
import os
import re

headers = {'user-agent': "alanuthuppan@yahoo.com"}
tableNumber = 1

def read_filing_links(excel_path):
    df = pd.read_excel(excel_path, sheet_name='Sheet1')
    return df['Filings URL'].tolist()

def get_soup_content(url):
    response = requests.get(url, headers=headers)
    return BeautifulSoup(response.content, 'html.parser')

def is_subtotal_row(row):
    first_cell = row.find('td')
    if first_cell and 'font-weight:700' in str(first_cell) and row.select_one('td[style*="border-top"]') is not None:
        subheader_text = first_cell.get_text(strip=True)
        if 'total' in subheader_text.lower():
            return False
    elif row.select_one('td[style*="border-top"]') is not None:
        return True
    else:
        return False

def process_table(soup, company_name, phrase):
    tables = soup.find_all(lambda tag: tag.name == 'table' and phrase in tag.text.lower() and company_name in tag.text)
    dataframes = []
    for table in tables:

        # Find the div/span containing the phrase within the table
        element_containing_phrase = table.find(lambda tag: tag.name in ["div", "span"] and "consolidated schedule of investment" in (tag.get_text() or '').lower())

        # If found and it's a div, get the next div sibling
        if element_containing_phrase and element_containing_phrase.name == 'div':
            next_div = element_containing_phrase.find_next_sibling('div')
            if next_div:
                date_text = next_div.get_text().strip()
        
        # If found and it's a span, split on br tags to get list of strings
        elif element_containing_phrase and element_containing_phrase.name == 'span':
            texts = element_containing_phrase.stripped_strings
            texts_list = list(texts)
            date_text = texts_list[texts_list.index("Consolidated Schedule of Investments") + 1].strip() if "Consolidated Schedule of Investments" in texts_list else None

        rows = table.find_all('tr')[3:]
        data = []
        headers = []
        current_investment_type = ""
        current_industry = ""

        for header in rows[0].find_all('td'):
            if header.find('span') is None:
                continue
            headers.append(header.get_text().strip())

        headers.insert(1, 'Investment Type')
        headers.insert(2, 'Industry')
        data.append(headers)


        for row in rows[1:]:
            if is_subtotal_row(row):
                continue

            first_cell = row.find('td')
            if first_cell and 'font-weight:700' in str(first_cell):
                subheader_text = first_cell.get_text(strip=True)

                if any(word in subheader_text.lower() for word in ['controlled', 'affiliated', 'debt', 'lien', 'equity', 'structure']) and 'total' not in subheader_text.lower():
                    current_investment_type = subheader_text.replace("(continued)", "").strip()
                elif 'total' not in subheader_text.lower():
                    current_industry = subheader_text.replace("(continued)", "").strip()
                continue

            row_data = [td.get_text(strip=True) for td in row.find_all('td') if td.find('span')]

            i = 0
            while i < len(row_data):
                item = row_data[i]

                if item == '' or item == '%':
                    row_data.pop(i)
                    if item == '%' and i > 0:
                        row_data[i - 1] += ' %'
                    continue

                if item == '$' or re.match(r'^[A-Z]{3}$', item) is not None:
                    if i + 1 < len(row_data):
                        row_data[i + 1] = item + ' ' + row_data[i + 1]
                    row_data.pop(i)
                    continue

                i += 1

            if len(row_data) > 0:
                row_data.insert(1, current_investment_type)
                row_data.insert(2, current_industry)
                row_data[4] = row_data[4] + "  " + str(row_data[5])
                row_data.pop(5)
                data.append(row_data)
            
        if data:
            df = pd.DataFrame(data)
            df.columns = df.iloc[0]
            df = df[1:]
            dataframes.append((df, date_text))

    return dataframes

def append_df_to_excel(filename, df, sheet_name, startrow=None, **to_excel_kwargs):
    # Check if file exists
    if not os.path.isfile(filename):
        df.to_excel(filename, sheet_name=sheet_name, startrow=startrow if startrow is not None else 0, index=False, header=True, **to_excel_kwargs)
        return
    
    # If the file exists
    with pd.ExcelWriter(filename, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
        # Check if sheet exists and append data
        if sheet_name in writer.book.sheetnames:
            startrow = writer.book[sheet_name].max_row
            df.to_excel(writer, sheet_name, startrow=startrow, index=False, header=False, **to_excel_kwargs)
        else:
            # If sheet does not exist, create new sheet and add data
            df.to_excel(writer, sheet_name, startrow=0, index=False, header=True, **to_excel_kwargs)


def autofit_column_widths(path):
    workbook = load_workbook(path)
    for sheet_name in workbook.sheetnames:
        sheet = workbook[sheet_name]
        for col in sheet.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    cell_length = len(cell.value)
                    max_length = max(max_length, cell_length)
                    cell.alignment = Alignment(horizontal='center')
                except:
                    pass

            max_length += 2
            sheet.column_dimensions[column].width = max_length

    workbook.save(path)

def main():
    filings_path = 'all_filings.xlsx'
    urls = read_filing_links(filings_path)
    output_excel = 'cleaned_soi_tables.xlsx'

    for url in urls:
        try:
            dataframes = process_table(soup, "Blackstone Private Credit Fund", "consolidated schedule of investment")

            for (df, date_text) in dataframes:
                append_df_to_excel(output_excel, df, sheet_name=date_text)
            
            break
        except Exception as e:
            with open('error_log.txt', 'a') as f:
                f.write(f"Error processing {url}: {str(e)}\n")
            soup = get_soup_content(url)

    autofit_column_widths(output_excel)


if __name__ == "__main__":
    main()