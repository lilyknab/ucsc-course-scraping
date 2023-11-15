from playwright.sync_api import sync_playwright, ViewportSize
from bs4 import BeautifulSoup
import re
import csv
import json
import unicodedata

year = ['Entering', '1st (frosh)', '2nd (soph)', '3rd (junior)', '4th (senior)', '1st (junior)', '2nd (senior)', '2nd(senior)']

url = 'https://catalog.ucsc.edu/en/current/general-catalog/academic-units/baskin-engineering/computer-science-and-engineering/computer-science-bs/'

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
    plannerwriter = csv.writer(csvfile)
    main = soup.find("div", {"id":"main"})
    for tag in main:
        if "B.S." in tag.text or "B.A." in tag.text:
            t = tag.text.strip("\n")
            year = t[0:7]
            tl = t.split('/ ')
            plannerwriter.writerow([year, tl[4]])
            break
    parent = soup.find("div", {"id":"degree-req-2"})
    currentyear = ""
    newYear = False
    for tag in parent:
        if tag.name == "h3" and tag.text[4:12] == "Planners":
            want = tag.next_sibling
            first_row = ['Fall', 'Winter', 'Spring', 'Summer']
            for child in want.descendants:
                if (child.name) == "p" and ("plan" in child.text or "Plan" in child.text) and (len(child.text) <= 100):
                    plannerwriter.writerow([child.text])
                if child.name == "table":
                    classes = [""]
                    nclasses = []
                    row = []
                    for g in child.descendants:
                        if g.name == "tr" and len(g.contents) != 11:
                            classes.append(currentyear)
                        elif g.name == "td":
                            t = unicodedata.normalize("NFKD", g.text)
                            t = t.strip()
                            if (t not in year and len(classes) % 5 != 1):
                                classes.append(t)
                            else:
                                if (t in year):
                                    currentyear=t
                                    
                                classes.append(currentyear)
                        
                    classes = classes[1:]
                    for entry in classes:
                        if len(row) == 5:
                            nclasses.append(row)
                            row = []
                        row.append(entry)
                    
                    for r in nclasses:
                        plannerwriter.writerow(r)
                    currentyear = ''
            break