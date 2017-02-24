# fileName: otheRegs.py
# Demonstrates regular expressions to locate and change key input parameter.
# This is an example of a script that pulls data, does work, then writes data.
# 
# J. Maynard 01/26/17

# Input: "iniFile.ini", "logFile.log"
# Output: Will update a scale parameter in the "iniFile.ini" file. 

import re
from shutil import copyfile
import datetime


DEBUG = True

# Set the path to the files. Assumes the files are in local directory
# during debugging. Real paths can be added here when the time is right. 

if DEBUG is True:
    logFile_path = "logFile.log"
    iniFile_path = "iniFile.ini"
# else:
# live paths here

def parse_data():
    """Grabs the values for n and a from
    the logFile.log file and gets current Scaling from the iniFile.ini file."""

    print '\nParsing data from logFile.log and iniFile.ini files.'
    last_line = file(logFile_path, "r").readlines()[-1]

    # Extracts 2 whatimlookingfor values from the last line
    pattern = '{whatimlookingfor=\d+\.\d+ exp=\d+'
    whatimlookingfor = re.findall(pattern, last_line)

    # Splits up the whatimlookingfor values because there are 2 of them
    ny = re.split(' ', whatimlookingfor[0])  # first one
    al = re.split(' ', whatimlookingfor[1])  # second one

    # Does some work
    # Cleans up the data and calculates the differences
    pattern = '(\d+\.\d+)|(\d+)'

    # Compares values for ny
    ny_measured = float(re.search(pattern, ny[0]).group())
    ny_exp = float(re.search(pattern, ny[1]).group())
    ny_diff = (ny_exp - ny_measured) / ny_exp

    # Compares values for al
    al_measured = float(re.search(pattern, al[0]).group())
    al_exp = float(re.search(pattern, al[1]).group())
    al_diff = (al_exp - al_measured) / al_exp

    # Scaling ------------------------------------------------------------------
    # Read the iniFile.ini file and get the curren Scaling value
    lines = file(iniFile_path, "r").readlines()
    
    # Sets a default
    scaling = 'ERROR: no match'
    
    # Finds the match for Scaling
    for l in lines:
        m = re.match('Scaling', l)
        if m is not None:
            scaling = l

    # More parsing and converts to a number
    scaling = float(re.search('\d+\.\d+E\d+', scaling).group())

    # Return a dictionary of values
    the_data = {'ny_measured': ny_measured,
                'ny_exp': ny_exp,
                'ny_diff': ny_diff,
                'al_measured': al_measured,
                'al_exp': al_exp,
                'al_diff': al_diff,
                'Scaling': scaling}

    return the_data
# We now have the data


def print_data(the_data):
    """Function for printing the data"""

    print '--------------------------------------------------------------------'
    the_scaling = '{0:.3E}'.format(the_data['Scaling'])
    # Strip the new line to match the nasty ini file formatting
    old_value = the_scaling.replace('+0', '')
    print 'Parsed Scaling value = ', old_value

    print '\nN measured = {0:.2f}'.format(the_data['ny_measured'])
    print 'N expected = {0:.2f}'.format(the_data['ny_exp'])
    print 'Difference = {0:.3%}'.format(the_data['ny_diff'])

    print '\nA measured = {0:.2f}'.format(the_data['al_measured'])
    print 'A expected = {0:.2f}'.format(the_data['al_exp'])
    print 'Difference = {0:.3%}'.format(the_data['al_diff'])
    print '--------------------------------------------------------------------'


def update_scale(the_data):
    """Back up the original file and writes the new value to the
    iniFile.ini file"""

    # Backup the file with time stamp
    # TODO: Clean up the time date formatting to simplify the file names
    dt = str(datetime.datetime.now())
    newname = 'ini_backup_' + dt + '.ini'
    copyfile("iniFile.ini", newname)

    # Calculate the new value by adjusting based on the % diff ny
    # This does work. 
    new_scale = the_data['Scaling'] * (1 + the_data['ny_diff'])

    # Format the value into the string
    sub_string = '{0:.3E}'.format(new_scale)
    # Strip the new line to match the iniFile.ini file formatting
    # TODO: not sure how to get python to format to drop the '+0' ?
    sub_string = sub_string.replace('+0', '')
    # Build the whole line to replace with end of line chars
    sub_string = "Scaling = " + sub_string

    print '\nCorrected scaling value = ', sub_string
    print "Writing new Scaling value to iniFile.ini file."

    # Write the iniFile.ini file with the new line -----------------------------
    # Read the file into a string
    the_file = open(iniFile_path, 'r')
    file_string = the_file.read()
    the_file.close()

    # Replace old value with the new value
    pattern = "Scaling = \d+\.\d+E\d+"
    file_string = (re.sub(pattern, sub_string, file_string))

    # Write the file back with new value
    the_file = open(iniFile_path, 'w')
    the_file.write(file_string)
    the_file.close()

if __name__ == "__main__":
    the_data = parse_data()
    print_data(the_data)
    update_scale(the_data)    

