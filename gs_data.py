# encoding=utf-8
""" gs_data centralizes all data import functions such as reading csv's
"""

import pandas as pd
import datetime as dt
from gs_datadict import *

def do_regions(ctydf: pd.DataFrame, mergef: str):
	"""
	do_regions assigns FIPS missing for multi-county regions, primarily occuring in UT where covid
	data is rolled up into 6 multi-county regions.  reading from a reference file, do_regions
	assigns FIPS and cumulative population for the region, and identifies member counties
	"""
	namecol = ctydf.columns.get_loc('County')
	state_idx = ctydf.loc[ctydf.State=='Utah'].index.to_list()
	nonnull_idx = ctydf.loc[(ctydf.State=='Utah') & (ctydf.FIPS>'')].index.to_list()
	# list comprehension finds rows which are missing a county FIPS
	null_idx = [x for x in state_idx if x not in nonnull_idx]
	merge_df = pd.read_csv(mergef, dtype={'fips0': str,'fips1': str,'fips2': str, 'fips3': str, 'fips4': str,'fips5': str})
	# add a column for county population, we'll add region pop here
	ctydf['Pop']= [None for x in range(len(ctydf))]
	ctydf['Multi_FIPS']= [[] for x in range(len(ctydf))]
	for x in null_idx:
		this_region = ctydf.iat[x,1]
		y = merge_df.loc[merge_df['Region']==this_region].to_dict('list')
		ctydf.iat[x,0]= y['fips0'][0]
		ctydf.iat[x,4]= y['Lat'][0]
		ctydf.iat[x, 5] = y['Long'][0]
		ctydf.iat[x, 9] = y['Long_Name'][0]
		ctydf.iat[x, 11] = y['Pop'][0]
		# make a list of county fips in the region, and add the list in column 'Multi-Fips' in master df
		z = [y['fips0'][0], y['fips1'][0]]
		if pd.notnull(y['fips2'][0]):
			z.append(y['fips2'][0])
			if pd.notnull(y['fips3'][0]):
				z.append(y['fips3'][0])
				if pd.notnull(y['fips4'][0]):
					z.append(y['fips4'][0])
					if pd.notnull(y['fips5'][0]):
						z.append(y['fips5'][0])
		ctydf.iat[x, 12] = z
		z = []
		y = {}
	# ALSO need to deal with Dukes and Nantucket region in MA:
	y = {'UID':[84070002], 'Region':['Dukes and Nantucket'], 'stFIPS':[25], 'Lat':[41.40674725], 'Long':[-70.68763497],
		 'Long_Name':['Dukes-Nantucket Region MA'], 'Pop':[28731], 'fips0':['25007'], 'fips1':['25019'],
		 'name0':['Dukes'], 'name1':['Nantucket'], 'pop0':[17332], 'pop1':[11399]}
	state_idx = ctydf.loc[ctydf.State=='Massachusetts'].index.to_list()
	nonnull_idx = ctydf.loc[(ctydf.State=='Massachusetts')&(ctydf.FIPS>'')].index.to_list()
	null_idx = [x for x in state_idx if x not in nonnull_idx]
	x = null_idx[0]
	this_region = ctydf.iat[x, 1]
	ctydf.iat[x, 0] = y['fips0'][0]
	ctydf.iat[x, 4] = y['Lat'][0]
	ctydf.iat[x, 5] = y['Long'][0]
	ctydf.iat[x, 9] = y['Long_Name'][0]
	ctydf.iat[x, 11] = y['Pop'][0]
	ctydf.iat[x, 12] = [y['fips0'][0], y['fips1'][0]]

	# final one is fixing Kansas City MO, not a rollup but for some reason it is sometimes outlier with no fips
	MO_merge = {'region_pop': [459787],
			 'region_name': ['Kansas City MO'],
			 'prior_fips': [29000],
			 'prior_names': ['Kansas City Missouri']
	}
	return ctydf

def get_countypop(popfile: str, excludefile: str):
	"""
	get_statepop builds a Dataframe, indexed on State Fips, with est 2020 population
	to avoid corrupting data, it then removes any counties which are part of a multi-county
	rollup for covid reporting
	"""
	dfpop = pd.read_csv(popfile, usecols={0,3}, dtype={'FIPS': str,'Pop': int})
	dfpop.set_index('FIPS', drop=True, inplace=True, verify_integrity=True)  # df has only fips index and Pop field
	dfpop.sort_index(inplace=True)
	excl = pd.read_csv(excludefile, usecols={7,8,9,10,11,12}, dtype={'fips0': str, 'fips1': str, 'fips2': str,
																	'fips3': str, 'fips4': str, 'fips5': str})
	for x in range(len(excl)):
		dfpop.drop(index=excl.iat[x, 0], inplace=True)
		dfpop.drop(index=excl.iat[x, 1], inplace=True)
		if pd.notnull(excl.iat[x, 2]):
			dfpop.drop(index=excl.iat[x, 2], inplace=True)
			if pd.notnull(excl.iat[x, 3]):
				dfpop.drop(index=excl.iat[x, 3], inplace=True)
				if pd.notnull(excl.iat[x, 4]):
					dfpop.drop(index=excl.iat[x, 4], inplace=True)
					if pd.notnull(excl.iat[x, 5]):
						dfpop.drop(index=excl.iat[x, 5], inplace=True)

	return dfpop

def get_counties(popdf: pd.DataFrame, jhucov: str, regionf: str):
	"""  get_counties reads in csv's and joins on 5-digit fips key
	:param popf: file containing population for each U.S. county (fips key)
	:type popf: str
	:param covf: covid data file by county, in this case Johns Hopkins
	:type covf: str
	:return: df
	:rtype: pd.DataFrame
	"""

	dfcov = pd.read_csv(jhucov, usecols=JHUC_COLNUM, dtype=JHUC_DTYPE, parse_dates=[3],
		dayfirst=False, infer_datetime_format=True)
	dfcov['Last_Update']= pd.to_datetime(dfcov['Last_Update'], format='%m/%d/%y', exact=True)
	dfcov = dfcov.rename(JHUC_RENAM)
	# deal with blank county FIPS, primarily in UT, do_regions handles these:
	dfcov = do_regions(dfcov, regionf)
	dfcov.dropna(inplace=True, subset=['FIPS'])
	dfcov.set_index('FIPS', drop=False, inplace=True, verify_integrity=True)
	dfcov.sort_index(inplace=True)

	df = dfcov.combine_first(popdf)
	df['DeathstoPop'] = 100*(df['Deaths'] / df['Pop'])
	df['CasestoPop'] = 100*(df['Confirmed'] / df['Pop'])
	# cleanup on aisle 'floats with NaN's'
	df['DeathstoPop'].fillna(value=0, inplace=True)
	df['CasestoPop'].fillna(value=0, inplace=True)
	df['DeathstoPop'] = pd.to_numeric(df['DeathstoPop'])
	df['CasestoPop'] = pd.to_numeric(df['CasestoPop'])
	return df

def get_nytcounty(popdf: pd.DataFrame, nytcov: str):
	"""
	get_nytcounty reads in county level covid data and reads county population data and adds a
	column for it
	"""

	dfnyt = pd.read_csv(nytcov, dtype={'fips':str,'county':str,'state':str}, parse_dates=[1],
		dayfirst=False, infer_datetime_format=True)
	dfnyt['date']= pd.to_datetime(dfnyt['date'], format='%m/%d/%Y', exact=True)
	dfnyt.dropna(inplace=True, subset=['fips'])
	dfnyt.set_index(['fips','date'], drop=False, inplace=True, verify_integrity=True)
	dfnyt.sort_index(inplace=True)

	return dfnyt

def get_statepop(stpopfile: str):
	"""
	get_statepop builds a Dataframe, indexed on State Fips, with est 2020 population
	"""
	df_st = pd.read_csv(stpopfile, usecols={1,2}, dtype={'pop':int})
	df_st.set_index('fips', drop=True, inplace=True)
	df_st.sort_index()
	return df_st

def get_states(df_pop: pd.DataFrame, jhu_stcov: str):
	"""
	:param df_pop: dataframe built in get county import, contains pop by county (fips)
	:type df_pop: pd.DataFrame
	:param covstate: csv file from jhu with state covid data
	:type covstate: fully qualified path/filename
	:return: df
	:rtype: pd.DataFrame
	"""
	dfst = pd.read_csv(jhu_stcov, dtype={'fips': str}, parse_dates=[3],
		dayfirst=False, infer_datetime_format=True)
	dfst['Last_Update'] = pd.to_datetime(dfst['Last_Update'], format='%m/%d/%y', exact=True)
	dfst.set_index('fips', drop=False, inplace=True, verify_integrity=True)
	dfst.sort_index(inplace=True)
	df = dfst.join(df_pop, how='left', lsuffix='', rsuffix='')
	df['fatalityrate'] = (df['Deaths'] / df['pop'])* 100
	df.round({'fatalityrate': 2})

	return df

def do_countystats(df: pd.DataFrame):
	"""
	computes descriptive stats on nyt county covid data
	initial df columns: fips,date,county,state,cases,deaths
	:param df: dataframe with time series county data
	:type df: df.DataFrame
	:param pop: dataframe with county fips and population
	:type pop: pd.Dataframe
	:return: df
	:rtype: pd.Dataframe
	"""
	asof = df.date.max()
	dfstats: pd.DataFrame = df.loc[df.date==asof]
	dfstats.set_index('fips', drop=False, append=False, inplace=True)
	fipslist = list(dfstats.fips.unique())

	for x in iter(fipslist):
		priormth: dt.date = asof - dt.timedelta(days=30)
		try:
			prior_row = df.loc[(str(x), priormth)]
		except KeyError:
			dfstats.at[dfstats['fips']==x, 'cases_30'] = None
			dfstats.at[dfstats['fips']==x, 'deaths_30'] = None
		else:
			dfstats.at[dfstats['fips']==x, 'cases_30'] = prior_row['cases']
			dfstats.at[dfstats['fips']==x, 'deaths_30'] = prior_row['deaths']
		priormth: dt.date = asof - dt.timedelta(days=60)
		try:
			prior_row = df.loc[(str(x), priormth)]
		except KeyError:
			dfstats.at[dfstats['fips']==x, 'cases_60'] = None
			dfstats.at[dfstats['fips']==x, 'deaths_60'] = None
		else:
			dfstats.at[dfstats['fips']==x, 'cases_60'] = prior_row['cases']
			dfstats.at[dfstats['fips']==x, 'deaths_60'] = prior_row['deaths']
		priormth: dt.date = asof - dt.timedelta(days=90)
		try:
			prior_row = df.loc[(str(x), priormth)]
		except KeyError:
			dfstats.at[dfstats['fips']==x, 'cases_90'] = None
			dfstats.at[dfstats['fips']==x, 'deaths_90'] = None
		else:
			dfstats.at[dfstats['fips']==x, 'cases_90'] = prior_row['cases']
			dfstats.at[dfstats['fips']==x, 'deaths_90'] = prior_row['deaths']

	dfstats.set_index('fips')
	dfstats.sort_index()
	dfstats['caserate'] = (dfstats['cases']/ dfstats['pop'])* 100
	dfstats['caserate'] = dfstats['caserate'].round(2)
	dfstats['ddtodc'] = ((dfstats['deaths']-dfstats['deaths_30'])/
						(dfstats['cases']-dfstats['cases_30']))
	dfstats['ddtodc'] = dfstats['ddtodc'].round(2)
	dfstats['ddtodc30'] = ((dfstats['deaths_30'] - dfstats['deaths_60'])/
						(dfstats['cases_30'] - dfstats['cases_60']))
	dfstats['ddtodc30'] = dfstats['ddtodc30'].round(2)
	dfstats['ddtodc60'] = ((dfstats['deaths_60'] - dfstats['deaths_90'])/
	                       (dfstats['cases_60'] - dfstats['cases_90']))
	dfstats['ddtodc60'] = dfstats['ddtodc60'].round(2)
	return dfstats
