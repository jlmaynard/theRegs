# fileName: otheRegs.py
# Demonstrates regular expressions to locate and change key input parameter.
# 
# J. Maynard 01/26/17

# Input: "iniFile.ini", "logFile.log"
# Output: Will update the scale parameter in the "iniFile.ini" file. 

import re
from shutil import copyfile
import datetime


DEBUG = True

# Set the path to the files. Assumes the files are in local directory
# during debugging. 

if DEBUG is True:
    logFile_path = "logFile.log"
    iniFile_path = "iniFile.ini"
# else:
# live paths here

def parse_data():
    """Grabs the measured and expected density for n and a from
    the logFile.log file and gets current Scaling from the iniFile.ini file."""

    print '\nParsing data from logFile.log and iniFile.ini files.'
    last_line = file(logFile_path, "r").readlines()[-1]

    # Extract the densities from the last line
    pattern = '{density=\d+\.\d+ exp=\d+'
    density = re.findall(pattern, last_line)

    # Splits them up by ny and al
    ny = re.split(' ', density[0])
    al = re.split(' ', density[1])

    # Cleans up the data and calculates the differences
    pattern = '(\d+\.\d+)|(\d+)'

    # print 'Checking density ranges (Nylon +/- 0.1%), (Al +/- 2.0%)'
    ny_measured = float(re.search(pattern, ny[0]).group())
    ny_exp = float(re.search(pattern, ny[1]).group())
    ny_diff = (ny_exp - ny_measured) / ny_exp

    al_measured = float(re.search(pattern, al[0]).group())
    al_exp = float(re.search(pattern, al[1]).group())
    al_diff = (al_exp - al_measured) / al_exp

    # outScaling ---------------------------------------------------------------
    # Read the iniFile.ini file and get the curren Scaling value
    lines = file(iniFile_path, "r").readlines()
    scaling = 'ERROR: no match'
    for l in lines:
        m = re.match('Scaling', l)
        if m is not None:
            scaling = l

    # If ny and al are within 5% of each other then perform the correction. If
    # not there is probably a bigger issue to reslove.
    if al_diff - ny_diff < .05:
        print "Values agree on percent difference."
        # Parse the scaling value
        scaling = float(re.search('\d+\.\d+E\d+', scaling).group())
    else:
        print "STOP - Density values too far off target! Check system HW."

    # Return a dictionary of values
    the_data = {'ny_measured': ny_measured,
                'ny_exp': ny_exp,
                'ny_diff': ny_diff,
                'al_measured': al_measured,
                'al_exp': al_exp,
                'al_diff': al_diff,
                'Scaling': scaling}

    return the_data


def print_data(the_data):

    print '--------------------------------------------------------------------'
    outscaling = '{0:.3E}'.format(the_data['Scaling'])
    # Strip the new line to match the dpp.ini file formatting
    old_value = outscaling.replace('+0', '')
    print 'Parsed Scaling value = ', old_value

    print '\nN measured = {0:.2f}'.format(the_data['ny_measured'])
    print 'N expected = {0:.2f}'.format(the_data['ny_exp'])
    print 'Difference = {0:.3%}'.format(the_data['ny_diff'])

    print '\nA measured = {0:.2f}'.format(the_data['al_measured'])
    print 'A expected = {0:.2f}'.format(the_data['al_exp'])
    print 'Difference = {0:.3%}'.format(the_data['al_diff'])
    print '--------------------------------------------------------------------'


def update_oscale(the_data):
    """Back up the original file and writes the new value to the
    iniFile.ini file"""

    # Backup the file with time stamp
    # TODO: Clean up the time date formatting to simplify the file names
    dt = str(datetime.datetime.now())
    newname = 'ini_backup_' + dt + '.ini'
    copyfile("iniFile.ini", newname)

    # Calculate the new outscaling by adjusting based on the % diff ny
    new_oscale = the_data['Scaling'] * (1 + the_data['ny_diff'])

    # Format the value into the string
    sub_string = '{0:.3E}'.format(new_oscale)
    # Strip the new line to match the iniFile.ini file formatting
    # TODO: not sure how to get python to format to drop the '+0' ?
    sub_string = sub_string.replace('+0', '')
    # Build the whole line to replace with end of line chars
    sub_string = "Scaling = " + sub_string

    print '\nCorrected scaling value = ', sub_string
    print "Writing new Scaling value to iniFile.ini file."

    # Write the iniFile.ini file with the new line
    # Read the file into a string
    the_file = open(iniFile_path, 'r')
    file_string = the_file.read()
    the_file.close()

    # Replace Scaling wiht new value
    pattern = "Scaling = \d+\.\d+E\d+"
    file_string = (re.sub(pattern, sub_string, file_string))

    # Write the file back with new Scaling value
    the_file = open(iniFile_path, 'w')
    the_file.write(file_string)
    the_file.close()


def first_pass():
    """This is the main function and performs the bulk of the work."""
    the_data = parse_data()
    print_data(the_data)
    update_oscale(the_data)


def second_pass():
    """We run this as a final check after running it again."""
    the_data = parse_data()

    # Test values to ensure N is within 0.1% and A is within 2.0%
    if (the_data['ny_diff'] <= 0.001) and (the_data['al_diff'] <= .02):
        print "\nScaling adjustment complete! Final values are:\n"
        print_data(the_data)
    else:
        print "STOP - Density values still off."


# Run the main() if this is the main file. -------------------------------------
if __name__ == "__main__":

    # Run the first pass and update outscaling
    first_pass()

    # Now run OTK again with new outScaling and re-test to ensure that
    # AL stays within range.
    print "\nACTION REQUIRED: Run it again to verify new values."
    test = raw_input("=> Ready to test new values after running it "
                     "with updated Scaling (Y/N)? ").lower()
    if test == "y":
        second_pass()
    else:
        print "TEST NOT COMPLETE - START OVER!"

# End main() -------------------------------------------------------------------
