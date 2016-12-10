from flask import Flask, render_template
app = Flask(__name__)

import pandas as pd
import numpy as np
#from sqlalchemy import create_engine
from bokeh.plotting import figure,output_file,show,vplot, ColumnDataSource
from bokeh.embed import components
from bokeh.models import HoverTool
from collections import OrderedDict

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
df_sorted['cum_rating'] = df_sorted['no_ratings'].cumsum()
df_sorted['perc_ratings']= 100*df_sorted['no_ratings']/df_sorted['no_ratings'].sum()
df_sorted['perc_books']= 100*df_sorted['cum_sum']/len(df_sorted)
df_sorted['cum_perc_ratings'] = df_sorted['perc_ratings'].cumsum()

# Bokeh tools
TOOLS = "resize,pan,wheel_zoom,box_zoom,reset,previewsave"

def make_figure1():
    plot = figure(tools=TOOLS
                  , width = 750
                  , height = 450
                  , title = 'the Long Tail'
                  , x_axis_label = 'Number of Books'
                  , y_axis_label = 'Number of Ratings'
                  , x_range = (-50,1080)
                 )
    plot.patch(pd.Series([0]).append(df_sorted['cum_sum'].append(pd.Series([0])))
            , pd.Series([0]).append(df_sorted['no_ratings'].append(pd.Series([0]))), color="#99d8c9")
    plot.line(df_sorted['cum_sum'], df_sorted['no_ratings'], color = 'Orange')

    source = ColumnDataSource(ColumnDataSource.from_df(df_sorted))
    
    hover = plot.select(dict(type=HoverTool))
    hover.tooltips = OrderedDict([
            ('Number of books', '@cum_sum'),
            ('Ratings', '@no_ratings')
        ]
    )
    
    return plot

def make_figure3():
    plot = figure(tools=TOOLS
                 , width = 750
                 , height = 450
                 , title = 'the Steep Climb'
                 , x_axis_label = 'Percentage of Total Books'
                , y_axis_label = 'Percentage of Total Ratings'
                 )
    plot.line(df_sorted['perc_books'], df_sorted['cum_perc_ratings'], color = 'Orange')
    
    source = ColumnDataSource(ColumnDataSource.from_df(df_sorted))
    
    hover = plot.select(dict(type=HoverTool))
    hover.tooltips = OrderedDict([
            ('Percentage of Total Books', '@perc_books'),
            ('Percentage of Total Ratings', '@cum_perc_ratings')
        ]
    )
    
    return plot

@app.route('/')
def hello_world():
    plot = vplot(make_figure1(), make_figure3())
    head = "Book Popularity"
    script, div = components(plot)
    return render_template('graph.html',script=script, div=div, head = head)

if __name__ == '__main__':
    app.run(port=33507)