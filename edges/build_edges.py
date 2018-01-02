#!/usr/bin/env python
# print "\nStarting up..."

import os
import pandas as pd
import itertools
from datetime import datetime
start_all_time = datetime.now()

################################################################################################################
################################################################################################################
# Set variables

committee_path = '../data/ORIGIN-GRADUATE_SCHOOL/dissertation_committees_2012-2017.xlsx'
faculty_path = '../data/ORIGIN-SCHOLARSATDUKE/ScholarsAtDuke_Faculty_October2017.xlsx'
output_path = './'

debug = False

# keep only primary appointments for a simpler graph
primary_only = False

# For display purposes
pd.set_option('display.max_rows', 200)
pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 1000)

if primary_only:
    print "\nOnly considering primary appointments"
    output_path += 'apt_primary/'
else:
    print "\nConsidering all non-admin appointments"
    output_path += 'apt_all/'

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

# drop otherwise unwanted / incorrect records
df_cm = df_cm.drop(df_cm[df_cm.Career != "GRAD"].index)
df_cm = df_cm.drop(df_cm[df_cm.Degree != "PHD"].index)

# drop any incomplete committees
students_to_remove = ["1838_2_1420_ELEC&CMP"] # has 10 members... likely two committees, just drop via hard coding
for student in df_cm.StudentIDFixed.unique():
    df_cm_student = df_cm[(df_cm.StudentIDFixed == student)]
    num_members = len(df_cm_student['Advisor Duke UID'].unique())
    if num_members < 4:
        students_to_remove.append(student)
        if debug:
            print "WARNING student %s only has %d members, dropping this student / committee" % (student, num_members)
            print df_cm_student

df_cm = df_cm.drop(df_cm[df_cm.StudentIDFixed.isin(students_to_remove)].index)

# clean date
df_cm['Confer Dt'] = pd.to_datetime(df_cm['Confer Dt'])
df_cm['Date'] = df_cm['Confer Dt'].dt.strftime('%Y-%m-%d')

# clean advisor DUID
# df_cm.fillna(value={'Advisor Duke UID': -1}, inplace=True) # change those without one to -1
df_cm.dropna(subset=['Advisor Duke UID'], inplace=True) # drop those without one
df_cm['AdvisorDUID'] = df_cm['Advisor Duke UID'].astype(int)

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

if debug:
    for student in df_cm.StudentIDFixed.unique():
        df_cm_student = df_cm[(df_cm.StudentIDFixed == student)]
        num_members = len(df_cm_student.AdvisorDUID.unique())
        if num_members > 6:
            print "WARNING student %s has %d members" % (student, num_members)
            print df_cm_student

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

if primary_only:
    df_fac = df_fac.drop(df_fac[df_fac.APPOINTMENT_TYPE != "P"].index)

# faculty not on a committee
df_fac = df_fac.drop(df_fac[~df_fac.DUID.isin(df_cm.AdvisorDUID.unique())].index)

# drop non-curricular organizational units
df_fac = df_fac.drop(df_fac[df_fac.ORGANIZATIONAL_UNIT.isin([50000280,50719999,50974566,50000387,50000388,50536159,50450124,50815429,50000642,50000300,50000761,50000844,50000845,51032158,50956932,50616932,50000608,50405998])].index)

# merge related units
df_fac['ORGANIZATIONAL_UNIT'].replace([50000414], 50000403, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50000472, 50896130, 50896131, 50896138, 50896140], 50000471, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50000518], 50000517, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50000551], 50413713, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50000812, 50000814, 50000815, 50000816], 50000811, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50000818], 50000817, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50000831], 50000830, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50000841, 50000842, 50000833, 50000836, 50000839, 50000843], 50000832, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50000859], 50000808, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50000871, 50000874, 50000888, 50000877, 50000886, 50000878, 50000880, 50000881, 50000875], 50000870, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50000912, 50000907, 50000913, 50000908, 50000906, 50000915, 50000909, 50000910, 50000905], 50000900, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50000930, 50000921, 50000922, 50000929, 50000931, 50000926, 50000932], 50000925, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50000940, 50000939, 50000941], 50000936, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50000952, 50000955, 50000958], 50000943, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50000966, 50000965, 50217368], 50000959, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50000982, 50000979, 50000973, 50000981, 50000977, 50000976], 50000972, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50000998, 50667814, 50000988, 50001001, 50001000, 50000994, 50000993, 50739563, 50688073, 50000995, 50000990], 50000983, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50001034], 50001029, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50001057], 50000850, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50043201], 50000810, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50084028], 50000496, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50084032], 50000528, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50084035], 50000554, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50193557], 50000857, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50293726, 50084030], 50000515, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50317277], 50000807, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50327914, 50418147, 50327915], 50000867, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50327917], 50327916, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50342261, 50342265, 50342272, 50000760], 50000758, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50362696, 50362697, 50362758, 50362691, 50000380], 50000379 , True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50432704], 50545114, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50496347, 50500096, 50500080, 50000526], 50500091, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50719993], 50000532, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50893727], 50000862, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50893744, 50893740, 50893742, 50893746, 50893739, 50893741, 50893745], 50893743, True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50986076], 50000991, True)

df_fac['ORG_DISPLAY_NAME'].replace(".*Human Vaccine Institute.*", 'Human Vaccine Institute', regex=True, inplace=True)
df_fac['ORG_DISPLAY_NAME'].replace(".*Law.*", 'Duke Law School', regex=True, inplace=True)
df_fac['ORG_DISPLAY_NAME'].replace("Anesthesiology.*", 'Anesthesiology', regex=True, inplace=True)
df_fac['ORG_DISPLAY_NAME'].replace("Community and Family Medicine.*", 'Community and Family Medicine', regex=True, inplace=True)
df_fac['ORG_DISPLAY_NAME'].replace("Institute for Decision and Statistical Science", 'Statistical Science', regex=True, inplace=True)
df_fac['ORG_DISPLAY_NAME'].replace("Medicine, Hematologic Malignancies and Cellular Therapy", 'Medicine, Hematology', regex=True, inplace=True)
df_fac['ORG_DISPLAY_NAME'].replace("Neurology.*", 'Neurology', regex=True, inplace=True)
df_fac['ORG_DISPLAY_NAME'].replace("Obstetrics and Gynecology.*", 'Obstetrics and Gynecology', regex=True, inplace=True)
df_fac['ORG_DISPLAY_NAME'].replace("Ophthalmology.*", 'Ophthalmology', regex=True, inplace=True)
df_fac['ORG_DISPLAY_NAME'].replace("Pediatrics.*", 'Pediatrics', regex=True, inplace=True)
df_fac['ORG_DISPLAY_NAME'].replace("Public Policy Studies", 'Sanford School of Public Policy', regex=True, inplace=True)
df_fac['ORG_DISPLAY_NAME'].replace("Radiology.*", 'Radiology', regex=True, inplace=True)
df_fac['ORG_DISPLAY_NAME'].replace("Sarah Stedman Nutrition & Metabolism Center", 'Medicine, Endocrinology, Metabolism, and Nutrition', regex=True, inplace=True)
df_fac['ORG_DISPLAY_NAME'].replace("Surgery.*", 'Surgery', regex=True, inplace=True)
df_fac['ORG_DISPLAY_NAME'].replace("Neurosurgery", 'Surgery', regex=True, inplace=True)
df_fac['ORG_DISPLAY_NAME'].replace(["Psychiatry & Behavioral Sciences.*", "Psychiatry, Child & Family Mental Health and Developmental Neuroscience"], 'Psychiatry & Behavioral Sciences', regex=True, inplace=True)
df_fac['ORG_DISPLAY_NAME'].replace("Immunology", 'Medicine, Immunology', regex=True, inplace=True)
df_fac['ORG_DISPLAY_NAME'].replace("Medicine, Rheumatology and Medicine, Immunology", 'Medicine, Immunology', regex=True, inplace=True)
df_fac['ORG_DISPLAY_NAME'].replace("Medicine, ", '', regex=True, inplace=True)

# Institutes and Provosts Academic Units | Nicholas Institute for Environmental Policy Solutions | 50312684
# Nicholas School of the Environment | Environmental Sciences and Policy | 50000480
df_fac['ORG_DISPLAY_NAME'].replace("Nicholas Institute for Environmental Policy Solutions", 'Environmental Sciences and Policy', regex=True, inplace=True)
df_fac['ORGANIZATIONAL_UNIT'].replace([50000483, 50312684], 50000480, True)
df_fac.loc[df_fac.ORGANIZATIONAL_UNIT == 50000480, 'SCHOOL_NAME'] = "Nicholas School of the Environment"


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

########################################################
# debugging code for cleaned df_fac
if debug:
    print "df_fac N rows = %d" % (len(df_fac.index))
    print "df_fac columns are:"
    for y in df_fac.columns:
        print (df_fac[y].name, df_fac[y].dtype, df_fac[y].iloc[0])
        # print (df_fac[y].name, df_fac[y].dtype)
        # print "'%s': %s," % (df_fac[y].name, df_fac[y].dtype)

    print "Number of unique faculty %d" % (len(df_fac.DUID.unique()))

if debug and not primary_only: # when only selecting P appointments, all of fac only have 1 row and it prints everyone...
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

if debug:
    print "\nListing all org units by name"
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

if debug:
    print "\nListing all org units by number"
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

if debug and False: # can't really fix these, don't have time to try to match by name...
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
# create lookup df to match ORGANIZATIONAL_UNIT to the human readable ORG_DISPLAY_NAME
df_org_names = df_fac[['ORGANIZATIONAL_UNIT', 'SCHOOL_NAME', 'ORG_DISPLAY_NAME']].drop_duplicates().sort_values('ORGANIZATIONAL_UNIT')

########################################################
# drop committee members who are not listed in faculty
df_cm = df_cm.drop(df_cm[~df_cm.AdvisorDUID.isin(df_fac.DUID.unique())].index)

########################################################
# merge the two data frames

if debug and False:
    print "\nRHS df to merge"
    print df_fac[['DUID', 'ORGANIZATIONAL_UNIT']].drop_duplicates().head(100)
    print "Done printing RHS df"

df_cm_merged = pd.merge(df_cm, df_fac[['DUID', 'ORGANIZATIONAL_UNIT']].drop_duplicates(),
how='left',
left_on = 'AdvisorDUID',
right_on = 'DUID',
sort=False,
suffixes=('_cm', '_fac')
)

# remove DUID since we already have AdvisorDUID
del df_cm_merged['DUID']

# remove advisors who are listed twice
if primary_only:
    df_cm_merged = df_cm_merged.drop_duplicates(subset=['StudentIDFixed', 'AdvisorDUID'])
else:
    df_cm_merged = df_cm_merged.drop_duplicates(subset=['StudentIDFixed', 'AdvisorDUID', 'ORGANIZATIONAL_UNIT'])

if debug and False:
    print "\nMerged df"
    print df_cm_merged.head(100)
    print "\nDone printing merged df"

################################################################################################################
################################################################################################################
# Create edges between ORGANIZATIONAL_UNITs from each committee
all_edge_rows_list = []
for student in df_cm_merged['StudentIDFixed'].unique():
    df_cm_student = df_cm_merged[(df_cm_merged.StudentIDFixed == student)]

    # get the date of the committee and do final checks on it's validity
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

    # now we are happy with the validity of the committee

    # save out all the edges we can make from the AdvisorDUIDs
    # itertools.combinations does what we want, produces all combinations of 2 commitee members
    edges = list(itertools.combinations(df_cm_student['ORGANIZATIONAL_UNIT'], 2))

    for edge in edges:
        this_row = {
        'Date': dates[0],
        'n1':edge[0],
        'n2':edge[1]
        }
        all_edge_rows_list.append(this_row)

# create df_edges
df_edges = pd.DataFrame(all_edge_rows_list)


########################################################
# debugging code for cleaned df_edges
if debug:
    print "df_edges N rows = %d" % (len(df_edges.index))
    print "df_edges columns are:"
    for y in df_edges.columns:
        print (df_edges[y].name, df_edges[y].dtype, df_edges[y].iloc[0])
        # print (df_edges[y].name, df_edges[y].dtype)
        # print "'%s': %s," % (df_edges[y].name, df_edges[y].dtype)

    print "Date min: %s" % (min(df_edges['Date']))
    print "Date max: %s" % (max(df_edges['Date']))


########################################################
print "\nNow saving out to %s" % (output_path)
make_path(output_path)

tag = "_all_appointments"
if primary_only: tag = '_primary_appointments'

df_edges.to_csv(output_path+"edges"+tag+".csv", index=False, na_rep='nan')
df_org_names.to_csv(output_path+"org_names"+tag+".csv", index=False, na_rep='nan')

if debug:
    make_path(output_path+"debug_dfs/")
    df_cm_merged.to_csv(output_path+"debug_dfs/df_cm_merged"+tag+".csv", index=False, na_rep='nan')
    df_cm.to_csv(output_path+"debug_dfs/df_cm"+tag+".csv", index=False, na_rep='nan')
    df_fac.to_csv(output_path+"debug_dfs/df_fac"+tag+".csv", index=False, na_rep='nan')

########################################################
print "\nFinished, exiting.\n"
print strfdelta(datetime.now()-start_all_time, "Total elapsed time: {hours} hours, {minutes} minutes, {seconds} seconds\n")
