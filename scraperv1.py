from playwright.sync_api import sync_playwright, ViewportSize
from bs4 import BeautifulSoup
import re
import csv
import json
import unicodedata

dont_want = ['Entering', '1st (frosh)', '2nd (soph)', '3rd (junior)', '4th (senior)', '1st (junior)', '2nd (senior)', '2nd(senior)']

#url = 'https://catalog.ucsc.edu/en/current/general-catalog/academic-units/baskin-engineering/computer-science-and-engineering/computer-science-bs/'
url = 'https://catalog.ucsc.edu/en/2020-2021/general-catalog/academic-units/baskin-school-of-engineering/computer-science-and-engineering/computer-science-bs/'

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    response_code = page.goto(url)
    if response_code.status != 200:
        print('error', response_code.status)

    html = page.content()
    soup = BeautifulSoup(html, 'html.parser')
    browser.close()

with open('planners.csv', 'w', newline='') as csvfile:
    planner_writer = csv.writer(csvfile)
    main = soup.find("div", {"id":"main"})
    for tag in main:
        if "B.S." in tag.text or "B.A." in tag.text:
            t = tag.text.strip("\n")
            year = t[0:7]
            tl = t.split('/ ')
            planner_writer.writerow([year, tl[4]])
            break
    
    max_row_len = 0
    max_row_contents = 0
    degree_req_num = ["2", "3", "4", "5"]
    for num in degree_req_num:
        parent = soup.find("div", {"id":"degree-req-"+num})
        if parent != None:
            current_year = ""
            newYear = False
            for tag in parent:
                if tag.name == "h3" and tag.text[4:12] == "Planners":
                    want = tag.next_sibling
                    first_row = ['Fall', 'Winter', 'Spring', 'Summer']
                    for child in want.descendants:
                        if (child.name) == "p" and ("plan" in child.text or "Plan" in child.text) and (len(child.text) <= 100):
                            planner_writer.writerow([child.text.strip()])
                        if child.name == "table":
                            classes = [""]
                            nclasses = []
                            row = []
                            for g in child.descendants:
                                if g.name == "tr":
                                
                                    if max_row_len == 0:
                                        if len(g.contents) == 11:
                                            max_row_len = 5
                                            max_row_contents = len(g.contents)
                                        else:
                                            max_row_len = 4
                                            max_row_contents = len(g.contents)
                                    if len(g.contents) != max_row_contents:
                                        classes.append(current_year)
                                elif g.name == "td":
                                    t = unicodedata.normalize("NFKD", g.text)
                                    t = t.strip()
                                    if (t not in dont_want and len(classes) % max_row_len != 1):
                                        classes.append(t)
                                    else:
                                        if (t in dont_want):
                                            current_year=t
                                            
                                        classes.append(current_year)
                                
                            classes = classes[1:]
                            for entry in classes:
                                if len(row) == max_row_len:
                                    nclasses.append(row)
                                    row = []
                                row.append(entry)
                            
                            for r in nclasses:
                                planner_writer.writerow(r)
                            current_year = ''
                            max_row_len = 0
                            max_row_contents = 0
                    break