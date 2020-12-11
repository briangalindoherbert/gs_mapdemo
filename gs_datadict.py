# encoding=utf-8
"""
gs_datadict contains collections to map the following:
    1. which fields to import from external files
    2. field names from imported files to preferred internal dataset names
    3. preferred dtypes for fields (or attributes-features-columns- synonymous terms)
    3. Order of fields (enhances readability and productivity)
"""
import pandas as pd
from typing import List, Dict, Set

# I have removed \n (end of line) from the grep patterns, as they are stripped prior to calling re.match
# for non-greedy matches (find first instance not longest), use suffix ? after multi-operator, as in *? or +?
# 1. nonUS: remove lines for non-U.S. entries (no FIPS AND Country_reg != US)
# 2. unassigned: remove lines for unassigned and 'out of' entries (5 digit FIPS starting with '9', ex. 90001)
# 3. puertorico: remove lines for Puerto Rico if states only desired (FIPS is 72xxx OR Admin2 = "Puerto Rico")
# 4. outof: remove line for 'out of <state name>' (5 digit FIPS starting with '8', ex. 80001)
# 5. nonstate: remove lines for guam, virgin islands and northern marianas (FIPS is two digits)
# 6. mod_padfips: pattern to find 4-digit FIPS and left-pad w/zero, SPLIT: | separates grep pattern from pseudo-code.
#                 to right of | is pseudo-code for other field mods. this is done to max re-use across source files
#   Pseudo-code how-to: each mod is enclosed in [], with elements delimited with : (colon)
#       element to left of colon is field or fields to mod, to the right of colon is operation to perform on the field
GREP_PREP: Dict = {"notUS":"^(,,)(.*?,)(.{0,20},)(.+)", "unassigned":"^(9\d{4},)(.+)", "puertorico":
                   "^(72\d{3},)(.+)", "outof":"^(8\d{4},)(.+)", "territory":"^(\d{2},)(.+)",
                   "mod_fips":"^(\d{4},)", "mod_date":"(\d{4}-\d{2}-\d{2})",
                   "non_grep":"[[11,12],round(x,3)]"}

JHUC_COLNUM: Set = set([0, 1, 2, 3, 5, 6, 7, 8, 9, 10, 12])
# above fields are: FIPS,County,State,Last_Update,Lat,Long,Confirmed,Deaths,Active,Combined_Key,Case_Fatality_Ratio
# skipped are 4.Country_Region and 11.Incident_Rate
JHUC_DTYPE: Dict = {'FIPS':str, 'Confirmed':int, 'Deaths':int, 'Active':int}
JHUC_RENAM: Dict = {'Combined_Key': 'Long_Name', 'Last_Update': 'Updated', 'Case_Fatality_Ratio': 'JHU_Fate_Rate'}

JHUC_ORDER: List = ['FIPS','Updated','County','State','Long_Name','Lat','Long','Pop','Confirmed','Deaths','Active',
                    'JHU_Fate_Rate', 'CasestoPop', 'DeathstoPop']

"""
these are definitions for Covid Tracking Project files- there are state and national files, current and time series
CTPST_COLNUM: Set = set([0, 1, 5, 6, 8, 16, 19, 20, 22, 23, 24, 28, 30, 31])
# CTP_COL_NUMS: FrozenSet = frozenset(["0", "1", "5", "6", "8", "16", "19", "20", "22", "23", "24", "28", "30", "31"])
CTPST_RENAM = dict(
	{"date": "Date", "state": "State", "hospitalizedCurrently": "curHosp", "hospitalizedCumulative": "aggHosp",
	 "inIcuCumulative": "aggICU", "death": "aggDeaths", "totalTestsViral": "aggResults",
	 "positiveTestsViral": "aggPosTest", "positiveCasesViral": "aggVCases", "fips": "FIPS",
	 "positiveIncrease": "dVCases", "totalTestResultsIncrease": "dResults", "deathIncrease": "dDeaths",
	 "hospitalizedIncrease": "daggHosp"})
CTPST_ORDER: List = ['Date', 'State', 'FIPS', 'aggResults', 'dResults', 'aggPosTest', 'dPosTest', 'dailyPosRate',
                         'aggVCases', 'dVCases', 'curHosp', 'aggHosp', 'daggHosp', 'aggICU', 'daggICU', 'aggDeaths',
                         'dDeaths']
                         
here is some now unused stuff for the multi-county merge, until I am certain of the functionality of do_regions
index=["49005", "49039", "49019", "49053", "49047", "49057"]
	UT_mc = {'region_pop': [186818, 81954, 40229, 252042, 272337, 272337],
			'region_name': ['Bear River', 'Central', 'Southeastern', 'Southwestern', 'Tri-County', 'Weber-Morgan'],
			'prior_fips': [[49003, 49033, 49005], [49039, 49027, 49031, 49055, 49023, 49041], [49007, 49019, 49015],
							[49053, 49025, 49017, 49021, 49001], [49047, 49013, 49009], [49057, 49029]],
			'prior_names': [['Box Elder', 'Rich', 'Cache'], ['Sanpete', 'Millard', 'Piute', 'Wayne', 'Juab', 'Sevier'],
							['Carbon', 'Grand', 'Emery'], ['Washington', 'Kane', 'Garfield', 'Iron', 'Beaver'],
							['Uintah', 'Duchesne', 'Daggett'], ['Weber', 'Morgan']],
			'prior_pop': [[56046, 2483, 128289], [30939, 13188, 1479, 2711, 12017, 21620], [20463, 9754, 10012],
							[177556, 7886, 5051, 54839, 6710], [35734, 19938, 950], [260213, 12124]]
			}

	MA_mc = {'region_pop': [28731],
			 'region_name': ['Dukes and Nantucket'],
			 'prior_fips': [25007, 25019],
			 'prior_names': ['Dukes', 'Nantucket'], 'prior_pop': [17332, 11399]
	}
"""
