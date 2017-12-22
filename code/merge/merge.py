#!/usr/bin/env python
# print "\nStarting up..."

import os
import pandas as pd
from datetime import datetime
start_all_time = datetime.now()

################################################################################################################
################################################################################################################
# Set variables

committees_path = '../data/ORIGIN-GRADUATE_SCHOOL/dissertation_committees_2012-2017.xlsx'
output_path = "./out.TODO"

debug = False

# For debugging purposes
# pd.set_option('display.max_rows', 200)
# pd.set_option('display.max_columns', 10)
# pd.set_option('display.width', 1000)

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
# end def for strfdelta

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
# end def for make_path

########################################################
# use this to automatically infer and print out each columns dtype

################################################################################################################
################################################################################################################
# start the real work

########################################################
# read in committee excel file
df_comm = pd.read_excel(committees_path) # , sheetname='Sheet1'

# create fixed / random unique student ID
df_comm['StudentIDFixed'] = df_comm.apply(lambda row: ('%s_%d_%d_%s' % (row['student random ID'], row['Degree Nbr'], row['Compl Term'], row['Acad Org'])), axis=1)

# Clean data and change column types
df_comm['Confer Dt'] = pd.to_datetime(df_comm['Confer Dt'])
df_comm['Date'] = df_comm['Confer Dt'].dt.strftime('%Y-%m-%d')

df_comm.fillna(value={'Advisor Duke UID': -1}, inplace=True)
df_comm['AdvisorDUID'] = df_comm['Advisor Duke UID'].astype(int)

df_comm = df_comm[(df_comm.Career == "GRAD")]
df_comm = df_comm[(df_comm.Degree == "PHD")]

# TODO split up Advisor Name into first / last?

# remove columns
# del df_comm['']
del df_comm['student random ID']
del df_comm['Confer Dt']
del df_comm['Advisor Duke UID']

del df_comm['Compl Term']
del df_comm['Compl Term Descr']
del df_comm['Degree Nbr']
del df_comm['Career']
del df_comm['Degree']
del df_comm['Advisor']

# drop duplicates
# Note: takes 10847 rows to 10823, not sure what is being lost but StudentIDFixed should be working
df_comm = df_comm.drop_duplicates()

# rename columns
df_comm.rename(columns={'Acad Prog': 'AcadProg', 'Acad Plan': 'AcadPlan', 'Acad Org': 'AcadOrg', 'Advisor Role': 'AdvisorRole', 'Advisor Name': 'AdvisorName'}, inplace=True)

if debug:
    print "df_comm N rows = %d" % (len(df_comm.index))
    print "df_comm columns are:"
    for y in df_comm.columns:
        print (df_comm[y].name, df_comm[y].dtype, df_comm[y].iloc[0])
        # print (df_comm[y].name, df_comm[y].dtype)
        # print "'%s': %s," % (df_comm[y].name, df_comm[y].dtype)

    print "Number of unique students %d" % (len(df_comm.StudentIDFixed.unique()))


print "Date min: %s" % (min(df_comm['Date']))
print "Date max: %s" % (max(df_comm['Date']))


# TODO now load faculty list


print "\nFinished, exiting.\n"
print strfdelta(datetime.now()-start_all_time, "Total elapsed time: {hours} hours, {minutes} minutes, {seconds} seconds\n")
