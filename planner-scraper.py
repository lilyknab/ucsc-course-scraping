from playwright.sync_api import sync_playwright, ViewportSize
from bs4 import BeautifulSoup
import csv
import unicodedata

PROXY = None

def write_major_name(csvwriter, elem, major_link):
    for tag in elem:
        if "B.S." in tag.text or "B.A." in tag.text or "B.M." in tag.text:
            crum = tag.text
            crum = crum.strip("\n")
            catalog_year = crum[0:7]
            crum_elements = crum.split('/')
            major_name = crum_elements[-1]
            major_name = major_name.strip()
            csvwriter.writerow([catalog_year, major_name, major_link])
            print(major_name)
            break
    
def set_planner_constants(row_len):
    max_row_len = 0
    max_row_contents = 0
    if row_len == 11:
        max_row_len = 5
        max_row_contents = row_len
    else:
        max_row_len = 4
        max_row_contents = row_len
    return max_row_len, max_row_contents

def get_match(string, substrings):
    for substring in substrings:
        if substring in string:
            return True
    return False

def get_table_entry(current_year, max_row_len, classes, text):
    school_year = ['entering', '1st', '2nd', '3rd', '4th', 'junior', 'senior', 'year']
    t = unicodedata.normalize("NFKD", text)
    t = t.strip()
    if (not get_match(t.lower(), school_year) and len(classes) % max_row_len != 1):
        classes.append(t)
    else:
        if (get_match(t.lower(), school_year)):
            current_year=t
        classes.append(current_year)
    return current_year

def get_planner_elements(child):
    classes = [""]
    max_row_len = 0
    current_year = ""
    for g in child.descendants:
        if g.name == "tr":
            row_len = len(g.contents)
            if max_row_len == 0:
                max_row_len, max_row_contents = set_planner_constants(row_len)
            if row_len != max_row_contents:
                classes.append(current_year)
        elif g.name == "td" or g.name == "th":
            current_year = get_table_entry(current_year, max_row_len, classes, g.text)        
    return classes[1:], max_row_len

def divide_planner_elements(classes, row_len):
    divided_classes = []
    row = []
    for entry in classes:
        if len(row) == row_len:
            divided_classes.append(row)
            row = []
        row.append(entry)
    return divided_classes

def write_planner_elements(csvwriter, divided_classes):
    for r in divided_classes:
        csvwriter.writerow(r)

def scrape_planners(csvwriter, soup_parent):
    for tag in soup_parent:
        if tag.name == "h3" and tag.text[4:12] == "Planners":
            next_tag = tag.next_sibling
            for child in next_tag.descendants:
                if (child.name) == "p" and ("plan" in child.text or "Plan" in child.text):
                    if (len(child.text) <= 100):
                        csvwriter.writerow([child.text.strip()])
                if child.name == "table":
                    classes, row_len = get_planner_elements(child)
                    divided_classes = divide_planner_elements(classes, row_len)
                    write_planner_elements(csvwriter, divided_classes)        
            break

def concat_link(link_fragment_list):
    concated_link = ""
    for string in link_fragment_list:
        concated_link += string
    return concated_link

def get_soup(link, proxy_server):
    with sync_playwright() as p:
        browser = p.chromium.launch(proxy={"server": proxy_server})
        page = browser.new_page()
        response_code = page.goto(link)
        if response_code.status != 200:
            print('error', response_code.status)
        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')
        browser.close()
    return soup


linkpt1 = 'https://catalog.ucsc.edu/en/'
linkpt2 = '/general-catalog/academic-programs/bachelors-degrees/'

#year_options = ['current', '2022-2023', '2021-2022', '2020-2021', '2019-2020']
year = 'current'
csvfilename = 'planners_' + year + '.csv'

def main():
    with open(csvfilename, 'w', newline='') as csvfile:
        planner_writer = csv.writer(csvfile)
        url = concat_link([linkpt1, year, linkpt2])
        soup = get_soup(url, PROXY)

        main = soup.find_all("a")
        for child in main:
            partial_link = str(child.get('href'))
            if ((year + '/General-Catalog/Academic-Units') in partial_link or (year + '/general-catalog/academic-units') in partial_link):
                major_link = concat_link([linkpt1, partial_link[4:]])

                soup = get_soup(major_link, PROXY)
                main = soup.find("div", {"id":"main"})
                write_major_name(planner_writer, main, major_link)
                
                page_nums = ["2", "3", "4", "5", "6"]
                for num in page_nums:
                    parent = soup.find("div", {"id":"degree-req-"+num})
                    if parent != None:
                        scrape_planners(planner_writer, parent)
                    else:
                        break

if __name__ == "__main__":
    main()