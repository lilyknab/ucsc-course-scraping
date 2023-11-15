from playwright.sync_api import sync_playwright, ViewportSize
from bs4 import BeautifulSoup
import csv
import unicodedata

year = ['Entering', '1st (frosh)', '2nd (soph)', '3rd (junior)', '4th (senior)', '1st (junior)', '2nd (senior)', '2nd(senior)']

#url = 'https://catalog.ucsc.edu/current/general-catalog/academic-units/baskin-engineering/biomolecular-engineering/biomolecular-engineering-and-bioinformatics-bs/'
url = 'https://catalog.ucsc.edu/en/current/general-catalog/academic-units/baskin-engineering/computer-science-and-engineering/computer-science-bs/'
#url = 'https://catalog.ucsc.edu/en/2021-2022/general-catalog/academic-units/social-sciences-division/economics/global-economics-ba/'

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    response_code = page.goto(url)
    if response_code.status != 200:
        print('error', response_code.status)

    html = page.content()
    soup = BeautifulSoup(html, 'html.parser')
    browser.close()

'''with open('planners.csv', 'w', newline='') as csvfile:
    plannerwriter = csv.writer(csvfile)'''
main = soup.find("div", {"id":"main"})
for tag in main:
    if "B.S." in tag.text or "B.A." in tag.text:
        t = tag.text.strip("\n")
        year = t[0:7]
        tl = t.split('/ ')
        #plannerwriter.writerow([year, tl[4]])
        print(year, tl[4])
        break

max_row_len = 0
max_row_contents = 0
degree_req_num = ["2", "3", "4", "5"]
for num in degree_req_num:
    parent = soup.find("div", {"id":"degree-req-"+num})
    if parent != None:
        current_year = ""
        for tag in parent:
            if tag.name == "h3" and tag.text[4:12] == "Planners":
                planners_head = tag.next_sibling
                for child in planners_head.descendants:
                    if (child.name) == "p" and ("plan" in child.text or "Plan" in child.text) and (len(child.text) <= 100):
                        #plannerwriter.writerow([child.text])
                        print(child.text)
                    if child.name == "table":
                        classes = []
                        for html_elem in child.descendants:
                            if html_elem.name == "tr":
                                
                                if max_row_len == 0:
                                    if len(html_elem.contents) == 11:
                                        max_row_len = 5
                                        max_row_contents = len(html_elem.contents)
                                        print('row len is', max_row_len)
                                        print('contents is', max_row_contents)
                                    else:
                                        max_row_len = 4
                                        max_row_contents = len(html_elem.contents)
                                        print('row len is', max_row_len)
                                        print('contents is', max_row_contents)
                                if len(html_elem.contents) != max_row_contents:
                                    classes.append(current_year)
                            elif html_elem.name == "td":
                                table_entry = unicodedata.normalize("NFKD", html_elem.text)
                                table_entry = table_entry.strip()
                                if (table_entry not in year and len(classes) % max_row_len != 1):
                                    classes.append(table_entry)
                                else:
                                    print('saving new year -', table_entry, '-')
                                    if (t in year):
                                        current_year = table_entry
                                    classes.append(current_year)
                        classes = classes[1:]
                        nclasses = []
                        row = []
                        for entry in classes:
                            if len(row) == max_row_len:
                                nclasses.append(row)
                                row = []
                            row.append(entry)
                        
                        for r in nclasses:
                            #plannerwriter.writerow(r)
                            print(r)
                        currentyear = ''
                        row_len = 0
                        max_row_contents = 0
                break
    else:
        break
