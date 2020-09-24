import os
import sys
import glob 
import shutil 
import subprocess 


class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

def run_cmd(cmd, exit_nonzero=False):
    """Helper function to spawn a subproces. If exit_nonzero is True, a nonzero return code results in program termination.
    """
    sp = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout_, stderr_ = sp.communicate()
    return_code = sp.returncode
    if return_code !=0 and exit_nonzero:
        print(f"Error running: {cmd}")
    
    print("stdout " + str(stdout_, sys.stdout.encoding))
    print("stderr " + str(stderr_, sys.stdout.encoding))

    return return_code, stdout_, stderr_


def buildAndTest(submissionpath, sourceTestPath):
    
    script_path = os.path.dirname(os.path.realpath(__file__))

    # create temporary directory so that previous students' results will not affect subsequent tests
    testCasePath = sourceTestPath

    testCases = glob.glob(os.path.join(testCasePath, "*.toy"))
    print(f"testCases {testCases}")

    for i in glob.glob(os.path.join(submissionpath, "*.o")):
        if os.path.exists(i):
            os.remove(i)
    progname = os.path.join(submissionpath, "toy")
    if os.path.exists(progname):
        os.remove(progname)

    if len(testCases) == 0:
        print("# no tests found.  double-check your path: " + testCasePath)
        sys.exit()

    print("# the following are all the commands run by this test script.  you can cut-and-paste them to run them by hand.")

    if os.path.exists(submissionpath + "/toy"):
        os.remove(submissionpath + "/toy")
    print("# building your toy compiler")
    print("make")
    out = subprocess.run(['make'], cwd = submissionpath,
            stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)

    output = ""
    err = ""
    if out.returncode != 0:
        output += "# ERROR running make failed."  
        print(output + " Do you have a Makefile?") # can't even compile the compiler 
        return None, None, output
        
    toyCompiler = os.path.join(submissionpath, "toy")
    totalCount = 1
    errorCount = 0
    
    # simpleC compilers lives so lets go through every test case now
    for case in testCases:
        print(f"testing case {case}")

        with cd(submissionpath):
            cmd = "cat /vagrant/grader-project/tests/1.toy | ./toy > temp"
            run_cmd(cmd)
            cmd = "cat /vagrant/template_start.s temp /vagrant/template_end.s > student.s"
            print(f"running cmd {cmd}")
            return_code, stdout, stderr = run_cmd(cmd,False)
            cmd = "diff -w -B student.s /vagrant/grader-project/tests/1.s"
            return_code, stdout, stderr = run_cmd(cmd,False)
            if len(str(stdout,sys.stdout.encoding)) == 0:
                print("Success")
            else:
                print("diff failed")
                output += f"output from {cmd}\n"
                output +="STDOUT: " + str(stdout,sys.stdout.encoding) + '\n'
                output +="STDERR: " + str(stderr,sys.stdout.encoding) + '\n'
                errorCount += 1

    #     caseTestFile = case
    #     caseGroundTruth = case.replace(".toy",".groundtruth")
    #     caseGroundTruthErr = case.replace(".simplec",".groundtrutherr")
    #     caseLLfile = case.replace(".simplec",".ll")
    #     caseBinary = case.replace(".simplec","")
    #     outFile = case.replace(".toy",".s")
    #     errFile = case.replace(".simplec",".err")

    #     print("\n# TESTING " + caseTestFile)
    #     try:
    #         # args = ["bash", os.path.join(script_path, "compile.sh"), toyCompiler, case]
    #         # command = " ".join(args)
    #         # print(command)
    #         # out = subprocess.run(args, 
    #         #                      timeout=5, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)
    #         # if out.returncode != 0:
    #         #     err = error("compile.sh", case)
    #         #     print(err)
    #         #     output += err
    #         #     errorCount += 1
    #         #     continue
    #         # else: print ("# SUCCESS")

    #         if os.path.exists(caseGroundTruth):
    #             args = ["bash", os.path.join(script_path, "run.sh"), submissionpath]
    #             command = " ".join(args)
    #             print(command)
    #             out = subprocess.run(args,
    #                     timeout=5, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)
    #             if out.returncode != 0:
    #                 err = error("run.sh", caseLLfile)
    #                 print(err)
    #                 output += err
    #                 errorCount += 1
    #                 continue
    #             else: print ("# SUCCESS")
                
    #             args = ["diff", "--strip-trailing-cr", "-Z", caseGroundTruth, outFile]
    #             print(args)
    #             command = " ".join(args)
    #             print(command)
    #             out = subprocess.run(args) #, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)

    #             if out.returncode != 0: #if the test case fails diff, increment error counter 
    #                 err = error("diff", outFile)
    #                 print(err)
    #                 output += err
    #                 errorCount += 1 
    #             else: print ("# SUCCESS")
    #         elif os.path.exists(caseGroundTruthErr):
    #             with open(caseGroundTruthErr) as f:
    #                 lines = f.readlines()
    #                 match = '^' + lines[0].strip() + '$'
    #             # args = ["diff", "--strip-trailing-cr", "-Z", '--unchanged-group-format=""', r'--old-group-format="%<"', '--new-group-format=""', caseGroundTruthErr, errFile]
    #             # args = ["diff", "--strip-trailing-cr", "-Z", '--unchanged-group-format=', r'--old-group-format=%<', '--new-group-format=', caseGroundTruthErr, errFile]
    #             args = ["egrep", match, errFile]
    #             command = " ".join(["egrep", '"' + match + '"', errFile])
    #             print(command)
    #             out = subprocess.run(args) #, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)

    #             if out.returncode != 0: #if the test case fails diff, increment error counter 
    #                 err = error("grep", errFile)
    #                 print(err)
    #                 output += err
    #                 errorCount += 1 
    #             else: print ("# SUCCESS")
    #     except Exception as e:
    #         print(str(e))
    #         output += str(e) + "\n" 
    #         err = error("compile.sh", case)
    #         print(err)
    #         output += err
    #         errorCount += 1
    #         continue
        
    # value = totalCount - errorCount
    
    # test_pass = repr(value) + " test cases passed out of " + repr(totalCount)
    # print(test_pass)

    # output += test_pass
    value = totalCount - errorCount
    print(f"Total passed - errors: {value}")
    return totalCount, value, output 

def error(app, f):

    return "# ERROR " + app + " failed on " + f + "\n"
    

if __name__ == "__main__":

    try:
        submissionDirectory = sys.argv[1]
        sourceTestPath = sys.argv[2]
    except:
        print("USAGE: path/to/your/repo path/to/the/tests")
        print("example: ./ ../syllabus/projects/tests/proj0/")
        sys.exit()


    buildAndTest(submissionDirectory, sourceTestPath)

