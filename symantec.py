import tempfile
import os, os.path
import glob
import re
from datetime import date
from subprocess import Popen, PIPE

DESC_FIELD = 6
FILE_FIELD = 7
AV_VERS_REGEX = re.compile('(\d.*)')
AV_PATH_REGEX = os.path.normcase('\\'.join([os.environ['ALLUSERSPROFILE'], r"Symantec\Symantec Endpoint Protection\*"]))
LOGPATH_REGEX = os.path.normcase('\\'.join([AV_PATH_REGEX, "Data\Logs\AV", date.today().strftime('%m%d%Y.Log')]))

version = None

def resultfromlog(filename):
    result = None
    logfile = glob.glob(LOGPATH_REGEX)

    if not logfile:
        return "Unable to read logs"

    filename = re.compile(filename, re.I)

    with open(logfile[0], 'r') as fd:
        for line in reversed(fd.readlines()):
            try:
                entries = line.split(',')
                result = filename.search(entries[FILE_FIELD])
                if result: 
                    break
            except Exception as e:
                pass

    if not result:
        return "clean"

    try:
        description = entries[DESC_FIELD]
        return description if description else "clean"
    except IndexError:
        return "Unable to retrieve description string, check for fileformat"

def get_version():
    logfile = glob.glob(AV_PATH_REGEX)
    
    if not logfile:
        return "Unknown"

    for name in logfile:
        match = AV_VERS_REGEX.search(name)
        if match:
            break
        
    return match.group(1)

def get_scan_result(data):
    (fd, filename) = tempfile.mkstemp()
    tmpfile = open(filename, "wb")
    tmpfile.write(data)
    tmpfile.close()
    os.close(fd)
    p = Popen(["DoSCan", "/ScanFile", filename], stdout=PIPE)
    res, err = p.communicate()
    retcode = p.returncode
    try:
        os.unlink(filename)
    except:
        pass
    return resultfromlog(os.path.basename(filename))

def scan(sfile):
    res = {}
    if version == "":
        get_version()
    res['version'] = version
    res['result'] = get_scan_result(sfile.data)
    return res
