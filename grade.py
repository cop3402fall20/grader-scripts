import os
import re
import csv
import sys
import pytz
import shutil
from lib import Submission
import zipfile
import subprocess
from git import Repo, Git
from datetime import datetime, timedelta
from testSimplec import buildAndTest
from distutils.dir_util import copy_tree


source_path = os.path.dirname(os.path.abspath(__file__)) # /a/b/c/d/e


def print_update(update, i, l, repository):
    print(update + " " + str(i+1) + "/" + str(l) + ": " + repository)



def get_submissions():

    url = "https://github.com/cop3402fall20/"
    temp_dir = "./tmp/"
    
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

    os.mkdir(temp_dir)

    submissions = []
    with zipfile.ZipFile("./submissions.zip", "r") as ref:
        ref.extractall(temp_dir)

    for filename in os.listdir(temp_dir):
        with open(temp_dir + "/" + filename, "r") as f:
            data = f.read()
            name = re.search("(?<=\: )(.*?)(?=\<)", data).group(0)
            student_id = re.search("\d+", filename).group(0)
            
            try:
                repository = re.search("url=" + url + "(.*)\"", data).group(1)
                
                if ".git" in repository:
                    repository = repository.split(".")[0]
                if "/" in repository:
                    repository = repository.split("/")[0]
                current_submission = Submission(student_id, name, repository,"parsed",None, None)
                submissions.append(current_submission)

            except AttributeError:
                repository = re.search("url=(.*)\"", data).group(1)
                current_submission = Submission(student_id,name, repository,"Error Parsing Git Link",None, None)
                submissions.append(current_submission)
    
    shutil.rmtree(temp_dir)
    
    return submissions

# Creates student directories and clones the remote repositories
def make_repo(path, submission):
    
    url = "git@github.com:cop3402fall20/"
    
    try:
        os.mkdir(path)
    except OSError:
        submission.status  += "\ninvalid github link: " + submission.repo
        return False
    
    git = url + submission.repo + ".git"
    Repo.clone_from(git, path)

    return True
# Runs the modular test case script for each student and updates the grades
# accordingly
def run_test_cases(submissions, project):
    print("Running test cases")
    for i, submission in enumerate(submissions):
        if submission.path is not None:
        
            path = os.path.join(source_path, "student_repos", submission.repo)
            subprocess.run(['make', 'clean'], cwd = path,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            print_update("Grading", i, len(submissions), submission.repo)

            test_case_path = os.path.join(source_path, "tests", project)
            points,submission.grade = buildAndTest(path, test_case_path)
            
            if points is not None:
                submission.grade = points
                try:
                    date = Repo(path).head.commit.committed_date
                
                    late = calculate_late(date, int(project[-1]))
                    if late > 0:
                        print(f"Late point deduction of {late}")
                        est = pytz.timezone('US/Eastern')
                        # repository[4] += f"::late point deduction:{repository[3] * 0.5}"
                        # repository[3] *= 0.5
                except ValueError:
                    # repo may be empty
                    # repository[4] += f"repo has no commit history"
                    pass
                    
        est = pytz.timezone('US/Eastern')
        
        submission.status += "::Graded at " + str(datetime.now(est).strftime('%I:%M %p %m/%d/%Y'))



# Either clones the students repo or fetches the lastest data and checks out
# the specific project tag.
def pull_checkout(submissions, project):
    not_found = list()
    student_repos = "./student_repos/"
    checkout_pt = 0
    failed_make_repo = list()

    if os.path.isdir(student_repos):
        created_dir = False
    else:
        os.mkdir(student_repos)
        created_dir = True

    for i, submission in enumerate(submissions):
        if submission.repo is not None:
            path = student_repos + submission.repo

            if created_dir:  ## new repo
                if not make_repo(path, submission):
                    submission.repo = None
                    submission.status += "\nFailed Clone"
                    failed_make_repo.append(str(submission))
                    submission.path = path
                    continue
                print_update("Cloning", i, len(submissions),submission.repo)
            else:
                if os.path.isdir(path): # check if clone worked
                    # for remote in Repo(path).remotes:
                    #     remote.fetch()
                    #     print_update("Fetching", i,
                    #             len(submissions), submission.repo)
                    submission.status += "\n Fetched"
                    submission.path = path
                else:
                    if not make_repo(path, submission):
                        submission.repo = None
                        failed_make_repo.append(str(submission))
                        continue
                    print_update("Cloning", i, len(submissions),submission.repo)
        else:
            not_found.append(project + " not found.")
            submission.status += "\n repo not found"


def calculate_late(date, project):
    
    est = pytz.timezone('US/Eastern')

    due = [datetime(2020, 10, 16,23 , 59, 0, 0),
            datetime(2020, 10, 30, 23, 59, 0, 0),
            datetime(2020, 11, 13, 23, 59, 0, 0),
            datetime(2020, 12, 4, 23, 59, 0, 0),
            datetime(2019, 12, 5, 23, 59, 0, 0)]

    if date - est.localize(due[project]).timestamp() <= 0:

        return 0
    
    late = datetime.fromtimestamp(est.localize(due[project]).timestamp()) + timedelta(days=14)

    if date - late.timestamp() <= 0:
        return 5

    return 2

            
if __name__ == "__main__":
    project = sys.argv[1]
    submissions = get_submissions()
    pull_checkout(submissions, project)
    run_test_cases(submissions, project)



    for s in submissions:
        print(s)