import pandas as pd
    
df = pd.read_csv('course-list.csv')
df2 = pd.read_csv('courses-no-name.csv')

df = df[['subjectCode', 'courseNumber', 'courseTitle']]
df2 = df2[['subjectCode', 'courseNumber', 'creditNarrative', 'prereqNarrative']]

df3 = pd.merge(df, df2)

df3.to_csv('courses-all-data.csv', index = False)
