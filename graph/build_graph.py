#!/usr/bin/env python
# print "\nStarting up..."

import os
import pandas as pd
from datetime import datetime
start_all_time = datetime.now()

################################################################################################################
################################################################################################################
# Set variables

edges_path = '../outputs/edges.csv'
output_path = './'

debug = False

# my_nrows = 200 # for testing
my_nrows = None # run on all rows

# For display purposes
pd.set_option('display.max_rows', 200)
pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 1000)

################################################################################################################
################################################################################################################
# Define functions

########################################################
# print out our times nicely
def strfdelta(tdelta, fmt):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)
# end def for strfdelta()

########################################################
# Define a function to create the output dir
# If it already exists don't crash, otherwise raise an exception
# Adapted from A-B-B's response to http://stackoverflow.com/questions/273192/in-python-check-if-a-directory-exists-and-create-it-if-necessary
# Note in python 3.4+ 'os.makedirs(output_path, exist_ok=True)' would handle all of this...
def make_path(path):
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise Exception('Problem creating output dir %s !!!\nA file with the same name probably already exists, please fix the conflict and run again.' % output_path)
# end def for make_path()

################################################################################################################
################################################################################################################
# start the real work

################################################################################################################
# read in edges from csv
if(my_nrows is not None): print "Reading first %d rows of %s" % (my_nrows, edges_path)
else: print "Reading all rows of %s" % (edges_path)

# need to specify dtypes manually when reading many rows... Otherwise pandas wants to try to load all the rows into memory before inferring the dtype and you get a warning
df_edges = pd.read_csv(edges_path, dtype={
'Date': object,
'n1': int,
'n2': int
} , nrows=my_nrows)

########################################################
# 

print df_edges.head(20)

'''
########################################################
print "\nNow saving out to %s" % (output_path)
make_path(output_path)
df_edges.to_csv(output_path+"edges.csv", index=False, na_rep='nan')
'''

########################################################
print "\nFinished, exiting.\n"
print strfdelta(datetime.now()-start_all_time, "Total elapsed time: {hours} hours, {minutes} minutes, {seconds} seconds\n")
