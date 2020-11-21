# gs_mapdemo
gs_mapdemo displays ratios such as cases, deaths, and hospitalizatons per 100 population from Covid-19.  By incorporating population data and
time-series data it allows more insightful charting of the incidence and risks in local areas from Covid-19 than simply a charting of raw totals.

this is first drop of this app, a work-in-process
I focused on building an architecture that facilitates expansion of the data used (e.g. data_dict.py to standardize imports), 
and functional isolation of code (e.g. functions for data cleaning and wrangling, functions for plotting)

TODO: add other ratios and correlations, and enhance the use of features in plotly mapbox (see https://github.com/users/briangalindoherbert/projects/2)

>I wrote this app in **PyCharm Professional** with a python3.9 interpreter version. Primary external libraries: pandas, plotly 
>Raw Covid-19 data is from 3 excellent github repos:  **Johns Hopkins University, the Covid Tracking Project, and the New York Times.**
  >> Note: currently it is a separate process (github desktop) to do the daily pull of .csv files with raw data.
  >>I have written **grep search-replace code (BBEdit patternplayground) to prep the .csv files** (e.g. fixing state-county FIPS to be 5 DIGITS (2+3).
    TODO: bring etl process into the app BY pulling the data and running any cleanup in python
>gs_mapdemo imports population data from the U.S. Census, and mortality data by Cause of Death(Cod) from the CDC Wonder DB, as .csv files
>I built plots in **GoogleMaps, matplotlib, and plotly**, and plotly actually has a range of options across express, graph_objects, figure_factory...and
I found the mapbox choropleths in plotly.graph_objects to be the best for me.  My plots with the other libraries were preliminary and pretty hack so I didn't include them in this repo.

summary of functions in gs_mapdemo:
  imports state and county level covid data from public repos
  imports census data
  cleans up FIPS issues with multi-county reporting (there are 6 multi-county reporting regions in Utah, one multi-county in Mass.)
  calculates incidence ratios vs population and over time
  plots choropleths using the mapbox choropleth features in plotyly.graph_objects


Personal: I've been in software/telecom for years, but new to Python (18 months). I went back to school (Emory University), earned certificates 
in BigData Analytics and Machine Learning and these repos are my personal initiative to turn classroom knowledge into real skills building apps 
relevant to a current issue. I've written this code on my own time, it's my committment to make my 'career2.0' about Analytics, ML, and AI.
I welcome collaboration and **constructive critique**, My expertise is product management, so I'm sure this code could be rewritten better!
