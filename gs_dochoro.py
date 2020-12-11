# encoding=utf-8
"""
gs_dochoro has functions to generate county and state level choropleths using
plotly graph_objects lower-level interface.
Alternatives are Choropleth and Choroplethmapbox
both functions return a plotly go.figure object
"""
from urllib.request import urlopen
import json
from datetime import date
import plotly.graph_objects as go
import pandas as pd
pd.set_option('precision',3)
pd.set_option('display.float_format','{:.2f}'.format)
"""   this commented-out code is for color map mgmt - see plotly doc
cmapx = plt.cm.get_cmap('viridis')
cmapx_rgb = []
norm = plt.cm.colors.Normalize(vmin=0, vmax=255)
for i in range(0, 255):
    k = plt.cm.colors.colorConverter.to_rgb(viridis_cmap(norm(i)))
    viridis_rgb.append(k)
"""

def do_stateplot(df: pd.DataFrame, thru: date):
	"""
	do_stateplot creates a plotly figure object for a state-level plot of covid
	data keyed on 2-digit state fips codes
	:param df: a DataFrame keyed on state fips with covid and pop data
	:type df: pd.DataFrame
	:return: fig: a plotly.graph_objects figure
	:rtype: plotly figure object
	"""
	st_dict = dict({"1":"AL","2":"AK","4":"AZ","5":"AR","6":"CA","8":"CO","9":"CT","10":"DE","11":"DC","12":"FL","13":"GA","15":"HI",
	"16":"ID","17":"IL","18":"IN","19":"IA","20":"KS","21":"KY","22":"LA","23":"ME","24":"MD","25":"MA","26":"MI","27":"MN","28":"MS",
	"29":"MO","29":"MO","30":"MT","31":"NE","32":"NV","33":"NH","34":"NJ","35":"NM","36":"NY","37":"NC","38":"ND","39":"OH","40":"OK",
	"41":"OR","42":"PA","44":"RI","45":"SC","46":"SD","47":"TN","48":"TX","49":"UT","50":"VT","51":"VA","53":"WA","54":"WV","55":"WI",
	"56":"WY"})
	locs = []
	for x in iter(df.fips):
		locs.append(st_dict[x])
	df['text'] = "Total Deaths: "+ str(df['Deaths'].astype('int'))

	fig = go.Figure(data=go.Choropleth(locations=locs,
		locationmode='USA-states', z=df.fatalityrate.round(2),
		colorscale='Viridis', hovertext=df['text'],
		colorbar_title="Deaths per 100 residents"
		))

	fig.update_layout(hovermode="x unified"
		)
	fig.update_layout(title_text='covid mortality by State thru ' +
		thru.strftime('%m-%d-%Y')+ " -custom data analysis by Brian Herbert", geo_scope='usa'
		)
	return fig

def do_countyplot(df: pd.DataFrame, thru: date):
	"""
	do_countyplot instantiates a plotly figure object with a Choropleth. fyi colorscale can be set to built in continuous
	such as bluered, Viridis, or ylorrd, or TODO: custom discrete colorscales can be used
	:param df: county-level table of covid and population data
	:type df: pd.DataFrame
	:return: fig
	:rtype: a plotly.graph_objects figure object
	"""
	with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
		counties = json.load(response)
	fig = go.Figure(go.Choroplethmapbox(geojson=counties,
		locations=list(df['FIPS']), z=df.DeathstoPop,
		customdata=df.DeathstoPop.round(2),
		hovertext=df.County, marker_opacity=0.5, marker_line_width=0.1,
		colorscale="ylorrd",
		colorbar_title="Fatalities per 100 people"))

	fig.update_layout(mapbox_style="open-street-map", mapbox_zoom=3,
		mapbox_center={"lat": 37.0902, "lon": -95.7129})
	fig.update_layout(title_text='Covid-19 local mortality as of ' +
		thru.strftime('%m-%d-%Y')+ " -python code and analysis by Brian Herbert")
	fig.update_layout(margin={"r": 0, "t": 32, "l": 0, "b": 0})
	return fig

def do_nytcounty(df: pd.DataFrame, thru: date):
	"""
	do_nytcounty instantiates a plotly figure object with a Choropleth
	:param df: county-level table of covid data from New York Times
	:type df: pd.DataFrame
	:param pop: table of fips and population for all counties
	:type pop: pd.DataFrame
	:param thru: date of most recent data records
	:type thru: date
	:return: fig
	:rtype: a plotly.graph_objects figure object
	"""
	with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
		counties = json.load(response)
	fig = go.Figure(go.Choroplethmapbox(geojson=counties,
		locations=list(df['fips']), z=df.caserate.round(2), colorscale="Viridis",
		autocolorscale=True,
		hovertext=df.ddtodc, colorbar_title="Case Rate")
		)
	# fig.update_layout(hovermode="x unified")
	fig.update_layout(mapbox_style="carto-positron", mapbox_zoom=3,
		mapbox_center={"lat": 37.0902, "lon": -95.7129})
	fig.update_layout(title_text='covid impact as of ' +
		thru.strftime('%m-%d-%Y'))
	return fig

def do_casesplot(df: pd.DataFrame, thru: date):
	"""
	do_countyplot instantiates a plotly figure object with a Choropleth
	:param df: county-level table of covid and population data
	:type df: pd.DataFrame
	:return: fig
	:rtype: a plotly.graph_objects figure object
	"""
	with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
		counties = json.load(response)
	fig = go.Figure(go.Choroplethmapbox(geojson=counties,
		locations=list(df['FIPS']), z=df.CasestoPop,
		colorscale="ylorrd", hovertext=df.County,
		marker_opacity=0.5, marker_line_width=0.2,
		colorbar_title="Cases per 100people"))

	fig.update_layout(mapbox_style="carto-positron", mapbox_zoom=3,
		mapbox_center={"lat": 37.0902, "lon": -95.7129})
	fig.update_layout(title_text='Covid-19 case spread as of ' +
		thru.strftime('%m-%d-%Y') + " -python code and analysis by Brian Herbert")
	fig.update_layout(margin={"r": 0, "t": 32, "l": 0, "b": 0})
	return fig