import pandas as pd
import os
import re

def convert_value(value):
    # Convert values with only numbers to integer
    if re.match(r'^[\d,]+$', value):
        return int(value.replace(',', ''))
    
    # Convert percentage formatted values to float (0.xx format)
    elif '%' in value:
        try:
            return float(value.replace('%', '')) / 100
        except ValueError:
            pass

    # Convert float in text form to actual float
    try:
        return float(value)
    except ValueError:
        pass

    # If none of the above, return the value as is
    return value

def table_to_dataframe(table, date):
    data = []

    rows = table.find_all('tr')[3:]  # Skip the first row

    headers = []
    for header in rows[0].find_all('td'):
        if header.find('span') is None:
            continue
        headers.append(header.get_text().strip())
    data.append(headers)

    for row in rows[1:]:
        row_data = []
        for cell in row.find_all('td'):
            # Skip cells containing only '$' or '%'
            if cell.get_text().strip() in ["$", "%"]:
                continue

            # Check if the cell contains a span element, if not skip
            if cell.find('span') is None:
                continue

            # Skip cell if it contains a capitalized, three-letter text
            if len(cell.get_text()) == 3 and cell.get_text().isupper():
                continue

            cell_value = cell.get_text().strip()
            converted_value = convert_value(cell_value)
            row_data.append(converted_value)

        # Combine third and fourth cells and shift left
        if len(row_data) > 4:
            row_data[2] = str(row_data[2]) + '         ' + str(row_data[3])
            del row_data[3]
        
        # Append this row data to the overall data
        if row_data:
            data.append(row_data)
    
    # Convert to DataFrame
    df = pd.DataFrame(data[1:], columns=data[0])
    return (df, date)