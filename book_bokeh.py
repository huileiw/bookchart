from flask import Flask, render_template
app = Flask(__name__)

import pandas as pd
import numpy as np
#from sqlalchemy import create_engine
from bokeh.plotting import figure,vplot
from bokeh.embed import components

#engine = create_engine('postgresql://HelenWang@localhost:5432/scrape')
#df = pd.read_sql_query('select * from books', con = engine, index_col = 'id')

path = "https://www.dropbox.com/s/5m8hlwb8lokvwfn/scrape.csv?dl=1"
df = pd.read_csv(path, header = 0,index_col=0)

df2 = df[['title','no_ratings']].drop_duplicates(subset = ['title'], keep = 'last')
df2['title upp'] = df2['title'].str.upper()
df3 = df2.drop_duplicates(subset = ['title upp'], keep = 'last')
df3['no_ratings'] = df3['no_ratings'].str.replace(' Ratings','')
df3['no_ratings'] = df3['no_ratings'].str.replace(' Rating','')
df3['no_ratings'] = df3['no_ratings'].str.replace(',','')
df3['no_ratings']= df3['no_ratings'].convert_objects(convert_numeric=True)

df_sorted = df3.sort_values(by='no_ratings',ascending = False)
df_sorted['one'] = 1
df_sorted['cum_sum'] = df_sorted['one'].cumsum()
df_sorted['perc_ratings']= df_sorted['no_ratings']/df_sorted['no_ratings'].sum()

# Bokeh tools
TOOLS = "resize,pan,wheel_zoom,box_zoom,reset,previewsave"

def make_figure1():
    plot1 = figure(tools=TOOLS
                 , width = 750
                 , height = 450
                 , title = 'Book Popularity'
                 , x_axis_label = 'Number of Books'
                 )
    plot1.line(df_sorted['cum_sum'], df_sorted['no_ratings'], color = 'Orange', legend = 'Number of Ratings')
    
    return plot1

def make_figure2():
    plot2 = figure(tools=TOOLS
                 , width = 750
                 , height = 450
                 , title = 'Book Popularity'
                 , x_axis_label = 'Number of Books'
                 )
    plot2.line(df_sorted['cum_sum'], df_sorted['perc_ratings'], color = 'Orange', legend = 'Percentage of Total Ratings')
    
    return plot2

@app.route('/')
def hello_world():
    plot = vplot(make_figure1(), make_figure2())
    script, div = components(plot)
    return render_template('graph.html',script=script, div=div)

if __name__ == '__main__':
    app.run(debug=True)
