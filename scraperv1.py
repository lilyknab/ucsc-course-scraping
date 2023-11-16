from playwright.sync_api import sync_playwright, ViewportSize
from bs4 import BeautifulSoup
import re
import csv
import json
import unicodedata

def write_major_name(crum):
    crum = crum.strip("\n")
    catalog_year = crum[0:7]
    crum_elements = crum.split('/ ')
    major_name = crum_elements[4]
    planner_writer.writerow([catalog_year, major_name])

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

def get_table_entry(current_year, max_row_len, classes, text):
    school_year = ['Entering', '1st (frosh)', '2nd (soph)', '3rd (junior)', '4th (senior)', '1st (junior)', '2nd (senior)', '2nd(senior)']
    t = unicodedata.normalize("NFKD", text)
    t = t.strip()
    if (t not in school_year and len(classes) % max_row_len != 1):
        classes.append(t)
    else:
        if (t in school_year):
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
        elif g.name == "td":
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

def write_planner_elements(divided_classes):
    for r in divided_classes:
        planner_writer.writerow(r)

def scrape_planners(soup_parent):
    for tag in soup_parent:
        if tag.name == "h3" and tag.text[4:12] == "Planners":
            want = tag.next_sibling
            for child in want.descendants:
                if (child.name) == "p" and ("plan" in child.text or "Plan" in child.text) and (len(child.text) <= 100):
                    planner_writer.writerow([child.text.strip()])
                if child.name == "table":
                    classes, row_len = get_planner_elements(child)
                    divided_classes = divide_planner_elements(classes, row_len)
                    write_planner_elements(divided_classes)
                       
            break




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
            write_major_name(tag.text)
            break
    
    page_nums = ["2", "3", "4", "5"]
    for num in page_nums:
        parent = soup.find("div", {"id":"degree-req-"+num})
        if parent == None:
            break
        else:
            scrape_planners(parent)
        