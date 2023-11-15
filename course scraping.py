import logging
import pandas as pd
import json
import re
from lark import Lark, logger, Transformer

logger.setLevel(logging.WARN)

preqs_parser = Lark(r"""
    ?start: value

    ?value:  course
        |   altern
        |   joint
        |   sp
    
    
    
    course: DEPARTMENT SPACE NUMBER LETTER?
    altern: value " or " value
    joint: value " and " value
    sp: value " " value

    %import common.ESCAPED_STRING
    %import common.NUMBER
    %import common.LETTER
    %import common.WORD
    %import common.WS
    
    SEMICOLON: ";"
    DEPARTMENT: /[A-Z]{2,5}/
    SPACE: " "
    COMMA: ","
    PERIOD: "."


    %ignore SEMICOLON
    %ignore WS
    %ignore COMMA
    %ignore PERIOD

""", start="start")

class TreeToPreqs(Transformer):
    def course(self, s):
        return "".join(s)

    def altern(self, a):
        res = ["OR"]
        res.extend(a)
        return res

    def joint(self, j):
        res = ["AND"]
        res.extend(j)
        return res
    
    def sp(self, s):
        res = ["AND"]
        res.extend(s)
        return res
    
course_data = pd.read_csv('course-list.csv')

course_data = course_data[['subjectCode', 'courseNumber', 'creditNarrative', 'prereqNarrative']]

for row in course_data.itertuples():
    if row[2][0] == '2' and len(row[2]) >= 3:
        course_data.drop(row[0], inplace=True)
    else:
        original_text = str(row[4])
        trimmed_text = original_text
        if trimmed_text[0:17] == "Prerequisite(s): ":
            trimmed_text = trimmed_text[17:]
        new_text = trimmed_text.rstrip('.')
        pattern = r'\b[A-Z]{2,}+\s+\w+\b'
        courses = re.findall(pattern, new_text)
        if courses != []:
            try:
                course_data = course_data.replace({'prereqNarrative': original_text}, json.dumps(TreeToPreqs().transform(preqs_parser.parse(new_text))))
            except:
                pass

course_data.to_csv('from-csv.csv', index = False)