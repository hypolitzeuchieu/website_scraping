import time
from itertools import zip_longest
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup


def get_table_on_page(url: str):
    headers = {
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', attrs={"class": "table table-sm small align-middle ltw-cell-center"})
            if table:
                return table
            else:
                print('Table not found')
        else:
            print('Something went wrong')
    except Exception as e:
        print(f'Error to fetch content from {url} :{e}')


def get_all_data_on_page(table):
    table_data = []
    for line in table.find_all('tr'):
        line_data = []
        for cell in line.find_all('td'):
            line_data.append(cell.text.strip())
        table_data.append(line_data)

    column_name = []
    if table_data:
        column_name = table_data[0]
        table_data = table_data[1:]

    df = pd.DataFrame(table_data, columns=column_name)
    df.to_csv('first_page.csv', index=False, sep='\t')
    return table_data


def get_all_pages_urls() -> list:
    urls_list = []
    for i in range(1, 452):
        base_url = f"https://results.finishtime.co.za/results.aspx?CId=35&RId=30204&EId=1&dt=0&PageNo={i}"
        urls_list.append(base_url)
    return urls_list


def get_all_urls_on_page(table) -> list:
    links = []
    for row in table.find_all('td'):

        for link in row.find_all('a'):
            if 'href' in link.attrs:
                link = urljoin("https://results.finishtime.co.za/", link['href'])
                links.append(link)
            else:
                print(f"No 'href' attribute found in the following link: {link}")

    print(len(links))
    return links


def get_number_of_columns(table) -> int:
    max_columns = 0
    for row in table.find_all('tr'):
        cells = row.find_all('td')
        max_columns = max(max_columns, len(cells))
        return max_columns


def get_name_url_on_page(table) -> list:
    column_links = [[] for _ in range(get_number_of_columns(table))]
    for column_index in range(get_number_of_columns(table)):  # iterating each column in my column numbers
        for row in table.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) > column_index:   # check if column exist in table_row
                cell = cells[column_index]  # fetch the cell data
                links = cell.find_all('a', href=True)
                for link in links:
                    full_link = urljoin("https://results.finishtime.co.za/", link['href'])
                    column_links[column_index].append(full_link)
            else:
                print('column not found')
    fav = column_links[0]
    race_no = column_links[1]
    name = column_links[2]
    name1 = column_links[3]
    category = column_links[4]
    gender = column_links[5]
    no_name = column_links[6]

    zipped_data = zip_longest(fav, race_no, name, name1, category, gender, no_name, fillvalue='')
    df = pd.DataFrame(zipped_data, columns=['Favorite', 'Race Number', 'Name', 'Name1',
                                            'Category', 'Gender', 'No_name'])
    df.to_csv('url_on_page.csv', index=False, sep='\t')
    return column_links


def main():
    pages = get_all_pages_urls()
    for page in pages:
        print(f'We are on page :{page}')
        table = get_table_on_page(page)
        data = get_all_data_on_page(table=table)
        url_per_columns = get_name_url_on_page(table)
        time.sleep(3)


if __name__ == '__main__':
    print(main())
