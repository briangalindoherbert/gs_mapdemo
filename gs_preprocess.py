# encoding=utf-8
"""
gs_preprocess performs previously manual edits to raw data files (such as greps that I did in bbedit) to strip rows,
modify headers, and fix fields like FIPS codes.  This is intended to fully automate the process of updating datasets
and plots, previously after doing pulls in github desktop, quite a few manual and tedious edits had to be performed
before running this gs_mapdemo app.
"""
import re
import os
import csv
from gs_datadict import GREP_PREP

DATADIR: str = "rawdata"
ctyfile = os.path.join(DATADIR, '12-09-2020.csv')

def do_greps(this_row: list=[], grepf: dict={}):
	"""
	do_greps takes a list representing a single row from a data file, and a dictionary of grep patterns, and applies
	the grep patterns to the list. If pattern matches, do_greps returns None, notifying calling fx to delete the record.
	do_greps also allows values in columns of input data to be formatted, like FIPS codes or timestamp fields
	:param this_row: a list containing field values for one row of data
	:param grepf: a dictionary where values are grep patterns to compare to each row of data
	:return: this_row: either return validated list of field values or None for row to be deleted
	"""
	str_row: str = ",".join(str(x) for x in this_row)

	for name, pattern in grepf.items():
		# DEBUG: end of line is \n  --> is probably stripped and not passed, need to adapt grep patterns which
		#        were identifying lines with  ^  for line start and  \n  for end of line
		if (str(name).startswith("mod_fips")):
			# mod patterns use my 'pseudo-code' model where to the left of the | delimiter is a grep pattern
			# and to the right are other mods to perform.  see gs_datadict for info on pseudo code structure
			comp_ptrn = re.compile(pattern)
			if (comp_ptrn.search(str_row)):
					this_row[0] = str(this_row[0]).zfill(5)   # if 4-digit FIPS, left-pad a zero
		elif (str(name).startswith("mod_date")):
			comp_ptrn = re.compile(pattern)
			for x in range(len(this_row)):
				mtch = comp_ptrn.search(this_row[x])
				if mtch:
					# strip the time portion out of date-time fields
					this_row[x] = mtch[0]
		elif (str(name).startswith("non")):
			# these are non-grep modifications, specified with parsable code in the pattern dictionary
			x = 0.00
			cols = eval(pattern)[0]  # get the columns to perform operation on
			for colidx in range(len(cols)):
				if not len(this_row[cols[colidx]])>0:
					this_row[cols[colidx]] = 0
				else:
					x = float(this_row[cols[colidx]])
					this_row[cols[colidx]] = eval(pattern)[1]  # 2nd element of mod_code[1] is operator
		else:
			# others are grep patterns to indicate rows for deletion:
			comp_ptrn = re.compile(pattern)
			if (comp_ptrn.search(str_row)):
				# return None to calling fx to omit (delete) this row, and break processing if deleting row
				this_row = None
				break
	return this_row

def do_cty_prep(ctyf: str, grepf: dict):
	"""
	do_fileprep automates previously manual preparation of raw data files to be used by the gs_mapdemo app. integrating
	raw data updates into the gs_mapdemo analysis and plotting is faster, less error-prone and seamless
	:param ctyf:
	:param grepf: a text file in which each row contains a grep-based search and replace task to run on the data file
	:return: ctyf_edit: the raw data file cleaned up and ready to be read by pandas read_csv
	"""
	# this code appended 'done_' to the input file to create name for output file
	# # instead I am using standard output names (ex. jhu_counties.csv) which insulates downstream scripts from change
	# path_file = ctyf.split("/")
	# path_file[1] = "done_" + path_file[1]
	# outf: str = path_file[0] + "/" + path_file[1]
	outf = os.path.join(DATADIR, 'jhu_counties.csv')

	try:
		fw = open(outf, "w+")
	except FileExistsError:
		os.remove(outf)
		fw = open(outf, "w+")

	recs_deleted = []
	delete_count: int = 0
	csv.register_dialect('read_dlct', strict=True, skipinitialspace=True, doublequote=True, quoting=csv.QUOTE_MINIMAL,
						 quotechar='\"')

	with open(ctyf, mode='r+', newline='', encoding='utf-8') as csvread:
		# this block processes field names in the header for the data
		filereader = csv.reader(csvread, dialect='read_dlct')
		# I tried dialect='unix' but it created some unwanted characters in output file
		filewriter = csv.writer(fw, dialect='read_dlct')
		header_rec: list = next(filereader)
		# index will throw a ValueError if not found
		try:
			x = header_rec.index("Admin2")
			header_rec[x] = "County"
		except ValueError:
			print("Admin2 field not found in raw file")
		try:
			x = header_rec.index("Province_State")
			header_rec[x] = "State"
		except ValueError:
			print("Province_State not found in raw file")
		try:
			header_rec.remove("Country_Region")
			country_del = True
		except ValueError:
			country_del = False
			print("Country_Region column not found, not deleted")
		filewriter.writerow(header_rec)

		with open(outf, mode='w+', encoding='utf-8', newline='') as csvwrite:
			# first (header) row has already been written, so filereader continues with content rows on row 2
			# note: country col is deleted, shifting cols from original layout!
			for readrow in filereader:
				curr_row: int = filereader.line_num
				cols = len(readrow)
				if country_del:
					# if header columns were removed, column data can be removed here
					readrow.pop(3)
				# current grep patterns identify rows to be removed only, but could be used for row mods too
				print(readrow)
				grepped = do_greps(readrow, grepf)
				if grepped is not None:
					filewriter.writerow(readrow)
				else:
					delete_count += 1
					# keep a 'log' of removed records with row that was read (do_greps returns None row)
					recs_deleted.append(readrow)
	csvread.close()
	fw.close()

	print("*"*80)
	print("*     do_cty_prep executed on data file: %s " %(ctyf))
	print("* ")
	print("*     deleted rows: %5d      total rows: %5d " %(delete_count, curr_row))
	print("* ")
	print("*     processed file was output as: %s " %(outf))
	print("* ")
	print("*" * 80)
	# print(recs_deleted)
	return curr_row

def do_st_prep(stf: str, grepf: dict):
	"""
	like do_cty_prep, do_st_prep programmatically does cleanup on raw data files to prepare them for read_csv
	:param stf: the raw daily covid data at state level from jhu dataset
	:return: stf_edit: the raw file cleaned up and ready for import as a DataFrame
	"""
	# rename 'Province_State' to 'State'
	#
	outf = "fin_" + stf
	recs_deleted = []
	delete_count: int = 0
	csv.register_dialect('read_dlct', strict=True, skipinitialspace=True, quoting=csv.QUOTE_NONE, escapechar='\\')
	csv.register_dialect('write_dlct', lineterminator='\n', skipinitialspace=True)

	with open(stf,mode='r+') as csvread:
		filereader = csv.reader(csvread, delimiter=',', quotechar='"')
		with open(outf, 'w', encoding='utf-8', newline='\n') as csvwrite:
			filewriter = csv.writer(csvwrite)
			filereader = csv.reader(csvread, dialect='read_dlct')
			header_rec = next(filereader)
			# unlike index, find will not throw a ValueError if not found, instead it returns -1
			try:
				x = header_rec.index("Admin2")
				header_rec[x] = "County"
			except ValueError:
				print("Admin2 field not found in raw file")
			try:
				x = header_rec.index("Province_State")
				header_rec[x] = "State"
			except ValueError:
				print("Province_State not found in raw file")
			# let's take advantage of mucking about in the raw file and append a stamp to the record
			header_rec.append("preproc_stamp")
			for readrow in filereader:
				curr_row: int = filereader.line_num
				if (curr_row==1):
					# these are header fieldnames- make changes to names of attributes that will be imported here
					filewriter.writerow(header_rec)
				else:
					readrow.append(curr_row)
				grepped = do_greps(readrow, grepf)
				if grepped is not None:
					filewriter.writerow(readrow)
				else:
					delete_count += 1
					recs_deleted.append(readrow)
	csvread.close()
	csvwrite.close()
	print("*"*80)
	print("*     State file prep executed on data: %s " %(ctyf))
	print("* ")
	print("*     deleted rows: %5d " %(delete_count))
	print("*" * 80)
	return delete_count

print("raw data file to pre-process: %s" %(ctyfile))
print("pre-processed %d rows " %(do_cty_prep(ctyfile, GREP_PREP)))