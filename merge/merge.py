#!/usr/bin/env python
# print "\nStarting up..."

import os
import pandas as pd
from datetime import datetime
start_all_time = datetime.now()

################################################################################################################
################################################################################################################
# Set variables

committee_members_path = '../data/ORIGIN-GRADUATE_SCHOOL/dissertation_committees_2012-2017.xlsx'
output_path = "./out.TODO"

debug = False

# For debugging purposes
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
# Define a function to fix the student ID
def create_StudentIDFixed(StudentRandomID, DegreeNbr, ComplTerm, AcadOrg):
    StudentIDFixed_str = '%s_%d_%d_%s' % (StudentRandomID, DegreeNbr, ComplTerm, AcadOrg)
    StudentIDFixed_str = StudentIDFixed_str.replace(' ', '')
    return StudentIDFixed_str

################################################################################################################
################################################################################################################
# start the real work

########################################################
# read in committee members (cm) excel file
df_cm = pd.read_excel(committee_members_path) # , sheetname='Sheet1'

########################################################
# clean committee data

# create fixed / random unique student ID
df_cm['StudentIDFixed'] = df_cm.apply(lambda row: create_StudentIDFixed(row['student random ID'], row['Degree Nbr'], row['Compl Term'], row['Acad Org']), axis=1)

# clean date
df_cm['Confer Dt'] = pd.to_datetime(df_cm['Confer Dt'])
df_cm['Date'] = df_cm['Confer Dt'].dt.strftime('%Y-%m-%d')

# clean advisor DUID
# df_cm.fillna(value={'Advisor Duke UID': -1}, inplace=True) # change those without one to -1
df_cm.dropna(subset=['Advisor Duke UID'], inplace=True) # drop those without one
df_cm['AdvisorDUID'] = df_cm['Advisor Duke UID'].astype(int)

# drop otherwise unwanted / incorrect records
df_cm = df_cm.drop(df_cm[df_cm.Career != "GRAD"].index)
df_cm = df_cm.drop(df_cm[df_cm.Degree != "PHD"].index)
df_cm = df_cm.drop(df_cm[df_cm.StudentIDFixed == "1838_2_1420_ELEC&CMP"].index) # has 10 members... likely two committees, just drop

# TODO split up Advisor Name into first / last?

# remove unwanted columns
del df_cm['student random ID']
del df_cm['Confer Dt']
del df_cm['Advisor Duke UID']

del df_cm['Compl Term']
del df_cm['Compl Term Descr']
del df_cm['Degree Nbr']
del df_cm['Career']
del df_cm['Degree']
del df_cm['Advisor']

# drop duplicates
df_cm = df_cm.drop_duplicates()

# rename columns
df_cm.rename(columns={'Acad Prog': 'AcadProg', 'Acad Plan': 'AcadPlan', 'Acad Org': 'AcadOrg', 'Advisor Role': 'AdvisorRole', 'Advisor Name': 'AdvisorName'}, inplace=True)


########################################################
# debugging code for cleaned df_cm
if debug:
    print "df_cm N rows = %d" % (len(df_cm.index))
    print "df_cm columns are:"
    for y in df_cm.columns:
        print (df_cm[y].name, df_cm[y].dtype, df_cm[y].iloc[0])
        # print (df_cm[y].name, df_cm[y].dtype)
        # print "'%s': %s," % (df_cm[y].name, df_cm[y].dtype)

    print "Number of unique students %d" % (len(df_cm.StudentIDFixed.unique()))

    print "Date min: %s" % (min(df_cm['Date']))
    print "Date max: %s" % (max(df_cm['Date']))

    students_counts = df_cm['StudentIDFixed'].value_counts()
    max_student_count = students_counts.max()

    print "Max number of rows for one student: %d" % (max_student_count)
    print "Mode(s): "
    modes = df_cm['StudentIDFixed'].mode()

    # for mode in modes:
    #    print mode
    #    df_cm_mode = df_cm[(df_cm.StudentIDFixed == mode)]
    #    print df_cm_mode
    #    print ""


########################################################
# create new df with one row per column
all_comm_rows_list = []

for student in df_cm['StudentIDFixed'].unique():
    df_cm_student = df_cm[(df_cm.StudentIDFixed == student)]

    dates = df_cm_student.Date.unique()
    if len(dates) > 1:
        print "ERROR: Multiple Date in student = %s continuing!" % (student)
        continue

    acadprogs = df_cm_student.AcadProg.unique()
    if len(acadprogs) > 1:
        print "ERROR: Multiple AcadProg in student = %s continuing!" % (student)
        continue

    acadplans = df_cm_student.AcadPlan.unique()
    if len(acadplans) > 1:
        print "ERROR: Multiple AcadPlan in student = %s continuing!" % (student)
        continue

    acadorgs = df_cm_student.AcadOrg.unique()
    if len(acadorgs) > 1:
        print "ERROR: Multiple AcadOrg in student = %s continuing!" % (student)
        continue

    # 'Advisors' is a list of lists ['AdvisorDUID', 'AdvisorRole', 'AdvisorName']
    advisors_list = []

    # loop through all the rows of this student's records to collect the advisors
    for index, row in df_cm_student.iterrows():
        advisors_list.append([row['AdvisorDUID'], row['AdvisorRole'], row['AdvisorName']])

    this_row = {
    'StudentIDFixed': student,
    'Date': dates[0],
    'AcadProg':acadprogs[0],
    'AcadPlan':acadplans[0],
    'AcadOrg':acadorgs[0],
    'Advisors':advisors_list
    }
    all_comm_rows_list.append(this_row)


# create df_comm TODO
df_comm = pd.DataFrame(all_comm_rows_list)

print df_comm.head(5)


########################################################
# debugging code for cleaned df_comm
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



########################################################
# TODO now load faculty list




########################################################
print "\nFinished, exiting.\n"
print strfdelta(datetime.now()-start_all_time, "Total elapsed time: {hours} hours, {minutes} minutes, {seconds} seconds\n")
