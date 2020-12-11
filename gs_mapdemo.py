#encoding=utf-8
""" gs_mapdemo is my controller to run plotly choropleths with covid data
for U.S. states and counties.  I integrate 3 data sources from Github: the
CovidTrackingProject, NewYorkTimes, and Johns Hopkins School of Engineering
(Big Props to the many contributors @NYT, JHU, and CovidTracking!).

Other sources for fips, population data, public health and mortality, etc.
include USAFacts.org, CDC Wonder DB, and data.census.gov
NOTE: with some files I have regex replacements that I run in BBEdit, such
as to properly format or combine state and county fips codes

AS OF Nov 30:
preprocess  162
gs_mapdemo   68
gs_data     228
dochoro     128
Total LOC:  586
"""

import os

import pandas as pd
import plotly.graph_objects as go
from plotly.io import renderers
import datetime as dt
from gs_data import *
from gs_dochoro import *

# settings: some options treated as suggestions not mandates!
runimports = True
run_nytimport = False
run_state = False
run_county = True

renderers.default = 'browser'
pd.options.plotting.backend = 'plotly'
pd.set_option('precision',7)
pd.set_option('display.float_format','{:.2f}'.format)
pd.set_option('max_colwidth', 40)
pd.set_option("display.max_rows", 600)
pd.set_option('display.show_dimensions', True)

# declaration of input files
DATADIR: str = "rawdata"
popfile = os.path.join(DATADIR, 'CountyPop2019.csv')
ctyfile = os.path.join(DATADIR, 'jhu_counties.csv')
statefile = os.path.join(DATADIR, 'jhu_states.csv')
stpopfile = os.path.join(DATADIR, 'StatePop2020.csv')
nytcfile = os.path.join(DATADIR, 'us_counties.csv')
UT_regionfile = os.path.join(DATADIR, 'UT_multi-county_regions.csv')

if runimports:
	# import of input files and identification of latest timestamps
	ctypop = get_countypop(popfile, UT_regionfile)
	df  = get_counties(ctypop, ctyfile, UT_regionfile)
	stpop = get_statepop(stpopfile)
	df_st: pd.DataFrame = get_states(stpop, statefile)
	dcol_jhuc: int = df.columns.get_loc('Last_Update')
	date_jhu: dt.date = df['Last_Update'].max()
	date_jhus: dt.date = df_st['Last_Update'].max()

if run_nytimport:
	dfnyt = get_nytcounty(ctypop, nytcfile)
	date_nyt: dt.date = dfnyt['date'].max()

if run_state:
	go_st: go.Figure = do_stateplot(df_st, date_jhus)
	go_st.show()

if run_county:
	go_cty: go.Figure = do_casesplot(df, date_jhu)
	go_cty.show()
	go_ctymort: go.Figure = do_countyplot(df, date_jhu)
	go_ctymort.show()
