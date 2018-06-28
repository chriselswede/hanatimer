# -*- coding: utf-8 -*-
from datetime import datetime
from threading import Timer
import sys, time, os, subprocess


def printHelp():
    print("                                                                                                                                                    ")    
    print("DESCRIPTION:                                                                                                                                        ")
    print(" HANATimer executes continously a query and records the overall times and the server times. This can be useful in scenarios like:                   ")
    print(" 1. You want to understand if runtime is even over time or if there are certain time frames with significant response time increases.               ")
    print(" 2. You want to see if runtimes suffer from specific scenarios, e.g. an increased delta storage or a high resource consumption.                     ")
    print(" HANATimer's output lists	                                                                                                                       ")
    print(" 1. Overall time: Time spent for SAP HANA server processing, network communication and client processing                                            ")
    print(" 2. Server time:  Time spent for SAP HANA server processing                                                                                         ")
    print("                                                                                                                                                    ")
    print("                                                                                                                                                    ")
    print("INPUT ARGUMENTS:                                                                                                                                    ")
    print(' -sql    test query, this sql statement will be executed and timed, the statement has to be quoted, i.e. surrounded by two ", no default            ')
    print(" -ws     wait [seconds], how many seconds hanatimer waits after it is done with one execution to start next execution, default: 1                   ")
    print(" -tp     test period [hours], how many hours hanatimer will continously execute and time the sql statement, default: 1                              ")
    print(" -od     output directory, full path of the folder where all output files will end up (if the folder does not exist it will be created),            ")
    print("         default: '/tmp/hanatimer_output'                                                                                                           ")
    print(" -so     standard out switch [true/false], switch to write to standard out, default:  true                                                          ")
    print(" -k      DB user key, this has to be maintained in hdbuserstore, i.e. as <sid>adm do                                                                ")               
    print("         > hdbuserstore SET <DB USER KEY> <ENV> <USERNAME> <PASSWORD>                     , default: SYSTEMKEY                                      ")
    os._exit(1)
                  
def printDisclaimer():
    print("                                                                                                                                 ")    
    print("ANY USAGE OF HANATIMER ASSUMES THAT YOU HAVE UNDERSTOOD AND AGREED THAT:                                                         ")
    print(" 1. HANATimer is NOT SAP official software, so normal SAP support of HANATimer cannot be assumed                                 ")
    print(" 2. HANATimer is open source                                                                                                     ") 
    print(' 3. HANATimer is provided "as is"                                                                                                ')
    print(' 4. HANATimer is to be used on "your own risk"                                                                                   ')
    print(" 5. HANATimer is a one-man's hobby (developed, maintained and supported only during non-working hours)                           ")
    print(" 6  All HANATimer documentations have to be read and understood before any usage:                                                ")
    print("     a) SAP Note 2634449                                                                                                         ")
    print("     b) The .pdf file that can be downloaded at the bottom of SAP Note 2634449                                                   ")
    print("     c) All output from executing                                                                                                ")
    print("                     python hanatimer.py --help                                                                                  ")
    os._exit(1)                  
                  
######################## DEFINE FUNCTIONS ################################

def is_integer(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
        
def log(logfile, message, std_out):
    if std_out:
        print message
    logfile.write(message+"\n")   
    logfile.flush()
    
def checkAndConvertBooleanFlag(boolean, flagstring):     
    boolean = boolean.lower()
    if boolean not in ("false", "true"):
        print "INPUT ERROR: "+flagstring+" must be either 'true' or 'false'. Please see --help for more information."
        os._exit(1)
    boolean = True if boolean == "true" else False
    return boolean    
    
def main():
    #####################  CHECK PYTHON VERSION ###########
    if sys.version_info[0] != 2 or sys.version_info[1] != 7:
        print "VERSION ERROR: hanacleaner is only supported for Python 2.7.x. Did you maybe forget to log in as <sid>adm before executing this?"
        os._exit(1)

    #####################   DEFAULTS   ####################
    sql_query = ''                        # no default --> has to provide sql statement
    wait_seconds = 1                      # default: wait 1 second between executions
    test_period = 1                       # default: perform the test during 1 hour
    out_dir = "/tmp/hanatimer_output"     # default output directory
    std_out = "true"                      #print to std out
    dbuserkey = 'SYSTEMKEY' # This KEY has to be maintained in hdbuserstore  
                            # so that   hdbuserstore LIST    gives e.g. 
                            # KEY SYSTEMKEY
                            #     ENV : mo-fc8d991e0:30015
                            #     USER: SYSTEM    
    
    #####################  CHECK INPUT ARGUMENTS #################
    if len(sys.argv) == 1:
        print "INPUT ERROR: hanatimer needs input arguments. Please see --help for more information."
        os._exit(1) 
    if len(sys.argv) != 2 and len(sys.argv) % 2 == 0:
        print "INPUT ERROR: Wrong number of input arguments. Please see --help for more information."
        os._exit(1)
    for i in range(len(sys.argv)):
        if i % 2 != 0:
            if sys.argv[i][0] != '-':
                print "INPUT ERROR: Every second argument has to be a flag, i.e. start with -. Please see --help for more information."
                os._exit(1)    
    
    
    #####################   PRIMARY INPUT ARGUMENTS   ####################     
    if '-h' in sys.argv or '--help' in sys.argv:
        printHelp()   
    if '-d' in sys.argv or '--disclaimer' in sys.argv:
        printDisclaimer() 
     
    #####################   INPUT ARGUMENTS   ####################      
    if '-sql' in sys.argv:
        sql_query = sys.argv[sys.argv.index('-sql') + 1]
    if '-ws' in sys.argv:
        wait_seconds = sys.argv[sys.argv.index('-ws') + 1]
    if '-tp' in sys.argv:
        test_period = sys.argv[sys.argv.index('-tp') + 1]
    if '-od' in sys.argv:
        out_dir = sys.argv[sys.argv.index('-od') + 1]
    if '-so' in sys.argv:
        std_out = sys.argv[sys.argv.index('-so') + 1]
    if '-k' in sys.argv:
        dbuserkey = sys.argv[sys.argv.index('-k') + 1]    

    ############# OUTPUT DIRECTORY #########
    out_dir = out_dir.replace(" ","_").replace(".","_")
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir)     
     
    ############ CHECK AND CONVERT THE REST OF THE INPUT PARAMETERS ################ 
    ### std_out, -so
    std_out = checkAndConvertBooleanFlag(std_out, "-so")
    ### wait_seconds, -ws
    if not is_integer(wait_seconds):
        log("INPUT ERROR: -ws must be an integer. Please see --help for more information.", std_out)
        os._exit(1)
    wait_seconds = int(wait_seconds) 
    ### test_period, -tp
    if not is_integer(wait_seconds):
        log("INPUT ERROR: -tp must be an integer. Please see --help for more information.", std_out)
        os._exit(1)
    test_period = int(test_period) 
 
    ############ GET LOCAL HOST and SID ##########
    local_host = subprocess.check_output("hostname", shell=True).replace('\n','') #if virtual_local_host == "" else virtual_local_host
    SID = subprocess.check_output('whoami', shell=True).replace('\n','').replace('adm','').upper()  
 
    ################ START #################
    logfile = open(out_dir+"/hanatimerlog_"+datetime.now().strftime("%Y-%m-%d_%H-%M-%S"+".csv"), "a")
    log(logfile, "**********************************************************\n"+datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"\nhanatimer by "+dbuserkey+" on "+SID+"("+local_host+")\nThe query that was continously executed is\n   "+sql_query+"\nBefore using HANATimer please read the disclaimer!\n   python hanatimer.py --disclaimer\n**********************************************************", std_out) 
    log(logfile, "Start Time,            Overall Time [micro seconds],         Server Time [micro seconds]", std_out)
    now = time.time()
    end_of_test_period = now + test_period*3600
    while time.time() < end_of_test_period:
        startTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        times = subprocess.check_output('''hdbsql -j -A -U '''+dbuserkey+''' "'''+sql_query+'''"''', shell=True).splitlines(1)[-2]
        overall_time = times.split(";")[0].split(" ")[-2]
        server_time = times.split(";")[1].split(" ")[-2]
        log(logfile, startTime+",   "+overall_time+",                                  "+server_time, std_out)        
        time.sleep(float(wait_seconds))
    logfile.close()
              
if __name__ == '__main__':
    main()
                        

