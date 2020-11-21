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
	# locs = dict({"CA":1, "TX":2, "NY":3})
	fig = go.Figure(data=go.Choropleth(locations=df.Abbrev,
		locationmode='USA-states', z=df.Deaths.astype('int'),
		zmin=54, zmax=15000, colorscale='Viridis',
		hovertemplate = 'Deaths: %{z:5d}<br><extra></extra>'
	))

	fig.update_layout(hovermode="x unified"
		)
	fig.update_layout(title_text='covid impact by State thru ' +
		thru.strftime('%m-%d-%Y'), geo_scope='usa'
		)
	return fig

def do_countyplot(df: pd.DataFrame, thru: date):
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
		locations=list(df['FIPS']), z=df.DeathstoPop,
		customdata=df.DeathstoPop.round(2),
		hovertext=df.County, marker_opacity=0.5, marker_line_width=0.2,
		colorscale=[
		# I'd like to set this programmatically, I called df.DeathstoPop.describe() to get the distribution:
        # least values have color rgb(0, 0, 0)
        [0, "rgb(0, 0, 0)"],
        # up to 50th percentile:
        [0.01, "rgb(0, 51, 51)"],
		# up to 75th percentile
        [0.05, "rgb(102, 102, 102)"],
		# up to 75th percentile
        [0.07, "rgb(153, 51, 51)"],
 		# and high-end
        [0.09, "rgb(204, 51, 0)"],
        [0.75, "rgb(255, 0, 0)"]
    ],
		colorbar_title="Fatalities per 100 people"))

	fig.update_layout(mapbox_style="carto-positron", mapbox_zoom=3,
		mapbox_center={"lat": 37.0902, "lon": -95.7129})
	fig.update_layout(title_text='Covid-19 local mortality (data from JHU) as of ' +
		thru.strftime('%m-%d-%Y'))
	fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
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
		colorscale="Viridis", hovertext=df.County,
		autocolorscale=True, marker_opacity=0.5, marker_line_width=0,
		colorbar_title="Cases per 100people"))

	fig.update_layout(mapbox_style="carto-positron", mapbox_zoom=3,
		mapbox_center={"lat": 37.0902, "lon": -95.7129})
	fig.update_layout(title_text='Covid-19 case spread as of ' +
		thru.strftime('%m-%d-%Y'))
	return fig