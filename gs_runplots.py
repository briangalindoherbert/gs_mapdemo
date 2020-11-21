# encoding=utf-8
"""
this is a script to separate the running of plots on processed data from the import, wrangling, and calc work done in
gs_mapdemo.py.  I do a lot of customization on the plotting end that uses the same DataFrames, I don't need to do
that processing to test out minor plotting changes.
"""
import pandas as pd
from plotly.io import renderers
from gs_dochoro import *

runcounty = True
runnyt = False
runstate = True

renderers.default = 'browser'
pd.options.plotting.backend = 'plotly'
pd.set_option('precision',7)
pd.set_option('display.float_format','{:.2f}'.format)
plotly_token = 'pk.eyJ1IjoiYmdoZXJiZXJ0IiwiYSI6ImNrYXl2MmFhYjBncHEyc3Bpa2ozczQwdGgifQ.glPFF4kjwrhP40bncFSnZA'

if runcounty:
	# go_cty = do_countyplot(df, updated)
	go_cty = do_casesplot(df, date_jhu)
	go_ctymort = do_countyplot(df, date_jhu)
	go_cty.show()
	go_ctymort.show()
if runnyt:
	df_nyt1 = do_countystats(df_nyt)
	go_nyt = do_nytcounty(df_nyt1, date_nyt)
	go_nyt.show()
if runstate:
	go_obj = do_stateplot(df_st, date_jhus)
	go_obj.show()
