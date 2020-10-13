import os
import subprocess
import sys

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
    stdout_, stderr_ = sp.communicate(timeout=1)
    return_code = sp.returncode
    if return_code !=0 and exit_nonzero:
        print(f"Error running: {cmd}")
    
    # print("stdout " + str(stdout_, sys.stdout.encoding))
    # print("stderr " + str(stderr_, sys.stdout.encoding))

    return return_code, str(stdout_, sys.stdout.encoding), str(stderr_, sys.stdout.encoding)



class Submission:
    def __init__(self, id, name, repo, status, path, grade):
        self.id = id
        self.name = name
        self.repo = repo
        self.status = status
        self.path = path
        self.grade = grade


    def __str__(self):
        
        #print("hi")
        return f"{self.id} {self.name} {self.repo} {self.status} {self.grade} {self.path} "