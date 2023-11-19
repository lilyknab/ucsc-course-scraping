# ucsc-course-scraping

add-course-name.py
    - uses csvreader and pandas to get name for each class in courses-no-name.csv
    - creates courses-all-data.csv

course-list-prereq-parser.py
    - uses csvreader and pandas to get course dept, code, credits, and prerequisites from course-list.csv
    - creates courses-no-name.csv

course-list.csv
    - list of UCSC courses, provided by the registrar

planner-scraper.py
    - uses playwright and bs4 to scrape UCSC planners from past catalog years
    - creates planners_{year}.csv