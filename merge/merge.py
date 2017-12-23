#!/usr/bin/env python
# print "\nStarting up..."

#import os
import pandas as pd
from datetime import datetime
start_all_time = datetime.now()

################################################################################################################
################################################################################################################
# Set variables

committee_path = '../data/ORIGIN-GRADUATE_SCHOOL/dissertation_committees_2012-2017.xlsx'
faculty_path = '../data/ORIGIN-SCHOLARSATDUKE/ScholarsAtDuke_Faculty_October2017.xlsx'
output_path = './'

debug = False

# For debugging display purposes
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
#def make_path(path):
#    try:
#        os.makedirs(path)
#    except OSError:
#        if not os.path.isdir(path):
#            raise Exception('Problem creating output dir %s !!!\nA file with the same name probably already exists, please fix the conflict and run again.' % output_path)
# end def for make_path()

########################################################
# Define a function to fix the student ID
def create_StudentIDFixed(StudentRandomID, DegreeNbr, ComplTerm, AcadOrg):
    StudentIDFixed_str = '%s_%d_%d_%s' % (StudentRandomID, DegreeNbr, ComplTerm, AcadOrg)
    StudentIDFixed_str = StudentIDFixed_str.replace(' ', '')
    return StudentIDFixed_str
# end def for create_StudentIDFixed()

########################################################
# Define a function to combine the faculty names
def combine_faculty_name(first, middle, last):

    first = first.encode('utf-8').replace(' ', '')
    middle = middle.encode('utf-8').replace(' ', '')
    last = last.encode('utf-8').replace(' ', '')

    middle = middle.replace('.', '')

    middle_initial = ''
    Name_str = ''
    if middle != "":
        middle_initial = middle[0].upper()
        Name_str = '%s,%s %s' % (last, first, middle_initial)
    else:
        Name_str = '%s,%s' % (last, first)

    return Name_str
# end def for combine_faculty_name()

################################################################################################################
################################################################################################################
# start the real work

################################################################################################################
# read in committee members (cm) excel file
df_cm = pd.read_excel(committee_path) # , sheetname='Sheet1'

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
if False and debug:
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


'''
########################################################
# create new df with one row per committee TODO is this what I want to do?? Revisit!!!
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


# create df_comm
df_comm = pd.DataFrame(all_comm_rows_list)


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

'''

################################################################################################################
# read in faculty (fac) excel file
df_fac = pd.read_excel(faculty_path) # , sheetname='Sheet1'

########################################################
# clean faculty data

# create simple name
df_fac.fillna(value={'PRO_FIRST_NAME': '', 'PRO_MIDDLE_NAME': '', 'PRO_LAST_NAME': ''}, inplace=True) # change those without one to an empty string
df_fac['FACULTY_NAME'] = df_fac.apply(lambda row: combine_faculty_name(row['PRO_FIRST_NAME'], row['PRO_MIDDLE_NAME'], row['PRO_LAST_NAME']), axis=1)

# drop unwanted records

# admin appointments
df_fac = df_fac.drop(df_fac[df_fac.APPOINTMENT_TYPE == "A"].index)

# faculty not on a committee
df_fac = df_fac.drop(df_fac[~df_fac.DUID.isin(df_cm.AdvisorDUID.unique())].index)

# drop non-curricular organizational units
df_fac = df_fac.drop(df_fac[df_fac.ORGANIZATIONAL_UNIT.isin([50000280,50719999,50974566,50000387,50000388,50536159,50450124,50815429,50000642,50000300,50000761,50000844,50000845,51032158,50956932,50616932,50000608,50405998])].index)

# merge units
df_fac['ORGANIZATIONAL_UNIT'].replace([50327917], 50327916, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50432704], 50545114, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50000818], 50000817, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50986076], 50000991, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50496347, 50500096, 50500080], 50500091, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50342261, 50342265, 50342272, 50000760], 50000758, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50000982, 50000979, 50000973], 50000972, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50000472, 50896130, 50896131, 50896138, 50896140], 50000471, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50293726, 50084030], 50000515, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50893727], 50000862, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50000414], 50000403, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50000483], 50000480, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50000518], 50000517, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50317277], 50000807, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50043201], 50000810, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50000812, 50000814, 50000815, 50000816], 50000811, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50000831], 50000830, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50000833, 50000836, 50000839, 50000843], 50000832, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50084028], 50000496, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50084032], 50000528, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50719993], 50000532, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50084035], 50000554, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50362696, 50362697, 50362758, 50362691, 50000380], 50000379 , True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50000871], 50000870, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50001034], 50001029, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50327914, 50418147, 50327915], 50000867, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50000952, 50000955, 50000958], 50000943, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50000841, 50000842, 50000958], 50000832, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50000940, 50000939, 50000941], 50000936, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50000922], 50000921, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50893744, 50893740, 50893742, 50893746, 50893739, 50893741, 50893745], 50893743, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50000966, 50000965, 50217368], 50000959, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50000981, 50000977, 50000976], 50000972, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50000998, 50667814, 50000988, 50001001, 50001000, 50000994, 50000993, 50739563, 50688073, 50000995], 50000983, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50000930, 50000921, 50000929, 50000931, 50000926, 50000932], 50000925, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50000912, 50000907, 50000913, 50000908, 50000906, 50000915, 50000909, 50000910], 50000900, True)

df_fac['ORG_DISPLAY_NAME'].replace(".*Law.*", 'Duke Law School', regex=True, inplace=True)
df_fac['ORG_DISPLAY_NAME'].replace(".*Human Vaccine Institute.*", 'Human Vaccine Institute', regex=True, inplace=True)
df_fac['ORG_DISPLAY_NAME'].replace("Anesthesiology.*", 'Anesthesiology', regex=True, inplace=True)
df_fac['ORG_DISPLAY_NAME'].replace("Community and Family Medicine.*", 'Community and Family Medicine', regex=True, inplace=True)
df_fac['ORG_DISPLAY_NAME'].replace("Neurology.*", 'Neurology', regex=True, inplace=True)
df_fac['ORG_DISPLAY_NAME'].replace("Obstetrics and Gynecology.*", 'Obstetrics and Gynecology', regex=True, inplace=True)
df_fac['ORG_DISPLAY_NAME'].replace("Ophthalmology.*", 'Ophthalmology', regex=True, inplace=True)
df_fac['ORG_DISPLAY_NAME'].replace("Surgery.*", 'Surgery', regex=True, inplace=True)
df_fac['ORG_DISPLAY_NAME'].replace("Radiology.*", 'Radiology', regex=True, inplace=True)
df_fac['ORG_DISPLAY_NAME'].replace("Psychiatry & Behavioral Sciences.*", 'Psychiatry & Behavioral Sciences', regex=True, inplace=True)


# remove unwanted columns
del df_fac['DISPLAY_NAME']
del df_fac['PRO_FIRST_NAME']
del df_fac['PRO_MIDDLE_NAME']
del df_fac['PRO_LAST_NAME']
del df_fac['APPOINTMENT_TITLE']
del df_fac['ORG_BFR_CODE']
del df_fac['SCHOOL_ORG_UNIT']
del df_fac['SCHOOL_BFR_CODE']

# drop duplicates
df_fac = df_fac.drop_duplicates()

# rename columns
# df_fac.rename(columns={'Acad Prog': 'AcadProg', 'Acad Plan': 'AcadPlan', 'Acad Org': 'AcadOrg', 'Advisor Role': 'AdvisorRole', 'Advisor Name': 'AdvisorName'}, inplace=True)


########################################################
# debugging code for cleaned df_fac
if False and debug:
    print "df_fac N rows = %d" % (len(df_fac.index))
    print "df_fac columns are:"
    for y in df_fac.columns:
        print (df_fac[y].name, df_fac[y].dtype, df_fac[y].iloc[0])
        # print (df_fac[y].name, df_fac[y].dtype)
        # print "'%s': %s," % (df_fac[y].name, df_fac[y].dtype)

    print "Number of unique faculty %d" % (len(df_fac.DUID.unique()))

if False and debug:
    faculty_appointment_counts = df_fac['DUID'].value_counts()
    max_faculty_appointment_count = faculty_appointment_counts.max()

    print "Max number of rows for one faculty member: %d" % (max_faculty_appointment_count)
    print "Mode(s): "
    modes = df_fac['DUID'].mode()

    for mode in modes:
        print mode
        df_fac_mode = df_fac[(df_fac.DUID == mode)]
        print df_fac_mode
        print ""

if False and debug:
    print "Listing all org unit info"

    for school_name in df_fac.SCHOOL_NAME.unique():
        df_fac_school = df_fac[(df_fac.SCHOOL_NAME == school_name)]

        for org_dis_name in df_fac_school.ORG_DISPLAY_NAME.unique():
            df_fac_school_dis_name = df_fac_school[(df_fac_school.ORG_DISPLAY_NAME == org_dis_name)]

            org_units = df_fac_school_dis_name.ORGANIZATIONAL_UNIT.unique()

            if len(org_units) > 1:
                # print "WARNING: Multiple org_units!"
                print "%s | %s | MULTIPLE" % (school_name, org_dis_name)
                print org_units
            elif len(org_units) > 0:
                print "%s | %s | %s" % (school_name, org_dis_name, org_units[0])
            else:
                print "\nno org units at all!!\n%s | %s" % (school_name, org_dis_name)

if False and debug:
    print "Listing all org units"

    for org in df_fac.ORGANIZATIONAL_UNIT.unique():
        df_fac_org = df_fac[(df_fac.ORGANIZATIONAL_UNIT == org)]

        school_names = df_fac_org.SCHOOL_NAME.unique()
        org_dis_names = df_fac_org.ORG_DISPLAY_NAME.unique()

        if len(school_names) > 1 or len(org_dis_names) > 1:
            print "%d | MULTIPLE" % (org)
            print school_names
            print org_dis_names
        else:
            print "%d | %s | %s" % (org, school_names[0], org_dis_names[0])

if False and debug:
    print "Find committee members not in faculty list"
    df_cm_not_in_fac = df_cm[~df_cm.AdvisorDUID.isin(df_fac.DUID.unique())]
    df_cm_not_in_fac = df_cm_not_in_fac[['AcadOrg', 'AdvisorDUID', 'AdvisorName']].drop_duplicates()

    N_missing_fac = len(df_cm_not_in_fac.index)
    if N_missing_fac > 0:
        print "Missing %d faculty!" % (N_missing_fac)
        print df_cm_not_in_fac
    else:
        print "No missing faculty"

########################################################
# drop committee members who are not listed in faculty
df_cm = df_cm.drop(df_cm[~df_cm.AdvisorDUID.isin(df_fac.DUID.unique())].index)


########################################################
# TODO Here we should roll up df_cm into one row per committee, getting rid of the faculty info and just keeping: date, subject / ORG_DISPLAY_NAME, and minimal meta data

########################################################
print "\nNow saving out to %s" % (output_path)

df_cm.to_csv(output_path+"cm.csv", index=False, na_rep='nan')
df_fac.to_csv(output_path+"fac.csv", index=False, na_rep='nan')

########################################################
print "\nFinished, exiting.\n"
print strfdelta(datetime.now()-start_all_time, "Total elapsed time: {hours} hours, {minutes} minutes, {seconds} seconds\n")
