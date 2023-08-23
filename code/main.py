from scraper import scrape
from extract import extract
from process import table_to_dataframe
from bs4 import BeautifulSoup
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Alignment
from openpyxl.styles import Font
from openpyxl import Workbook
import requests
import os

headers = {'user-agent': "alanuthuppan@yahoo.com"}

response = requests.get("https://www.sec.gov/Archives/edgar/data/1803498/000180349823000012/bcred-20230331.htm", headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')


def write_to_excel(df_tables):
    filename = "cleaned_soi_tables.xlsx"

    if os.path.exists(filename):
        book = load_workbook(filename)
    else:
        book = Workbook()
        del book["Sheet"]  # Remove default sheet

    for df, date in df_tables:
        suffix = 1
        sheet_name = f"{date}_{suffix}"

        # Check if the sheet already exists. If it does, find a new name
        while sheet_name in book.sheetnames:
            suffix += 1
            sheet_name = f"{date}_{suffix}"
            

        # Create new sheet
        ws = book.create_sheet(title=sheet_name)

        # Write data
        for r_idx, row in enumerate(df.values, 1):
            for c_idx, value in enumerate(row, 1):
                ws.cell(row=r_idx, column=c_idx, value=value)

        # Write headers
        for c_idx, header in enumerate(df.columns, 1):
            cell = ws.cell(row=1, column=c_idx, value=header)
            cell.font = Font(bold=True)

        # Adjusting the column widths
        for column in df:
            max_len = max(df[column].astype(str).apply(len).max(),  # max length in column
                          len(str(column))) + 2  # length of column header/title
            col_letter = get_column_letter(df.columns.get_loc(column) + 1)  # Get excel column letter
            ws.column_dimensions[col_letter].width = max_len

            # Aligning cell values to center
            for cell in list(ws[col_letter]):
                cell.alignment = Alignment(horizontal='center')

    book.save(filename)




# # Scrape the pages from the CIK 
# cik = 1803498
# filing_soups = scrape(cik)

# # Extract all the relevant tables and dates from each filing
# tables = []
# for soup in filing_soups:
#     result = extract.extract(soup)
#     if len(result) != 0:
#         tables.append(result)

tables = extract(soup, "Blackstone Private Credit Fund")

df_tables = []
for i in range(20):
    df_tables.append(table_to_dataframe(tables[i][0], tables[i][1]))

write_to_excel(df_tables)