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
from lib import cd, Submission, run_cmd
from canvas import comment_file
import time




source_path = os.path.dirname(os.path.abspath(__file__)) # /a/b/c/d/e


def print_update(update, i, l, repository):
    print(update + " " + str(i+1) + "/" + str(l) + ": " + repository)



def get_submissions(assignmentid):

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
                current_submission = Submission(student_id, name, repository,"parsed",None, None, assignmentid)
                submissions.append(current_submission)

            except AttributeError:
                repository = re.search("url=(.*)\"", data).group(1)
                current_submission = Submission(student_id,name, repository,"Error Parsing Git Link",None, None, assignmentid)
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
def run_test_cases(submissions, project, API_KEY, regrade=False):
    count = 0
    print("Running test cases")
    print(submissions)
    time.sleep(0.33)

    for i, submission in enumerate(submissions):
        
        if regrade and not submission.tag_exists:
             print(f"Skipping since submission tag for {project} does not exist")
             continue
        count += 1
        submission.grade = 0
        if submission.path is not None:
        
            path = os.path.join(source_path, "student_repos", submission.repo)
            subprocess.run(['make', 'clean'], cwd = path,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            print_update("Grading", i, len(submissions), submission.repo)

            test_case_path = os.path.join(source_path, "tests", project)
            points, output = buildAndTest(path, test_case_path, project)
            output = "Turned in +1 points\n" + output
            points += 1
            

            submission.grade = 1
            est = pytz.timezone('US/Eastern')
            commit_hash = None
            if points is not None:
                submission.grade = points
                try:
                    date = Repo(path).head.commit.committed_date
                    print(f"date: {date}")
                    print(commit_hash)
                    commit_hash = str(Repo(path).head.commit)
                
                    late = calculate_late(date, int(project[-1]))
                    if late > 0:
                        print(f"Late point deduction of {2}")
                        output += f"Late: -2 points\n"
                        submission.grade -= 2
                        
                        # repository[4] += f"::late point deduction:{repository[3] * 0.5}"
                        # repository[3] *= 0.5
                except ValueError:
                    commit_hash = "Error Getting commit. Is the repo empty?"
                    pass
            output += f"Using commit {commit_hash}\n"
            output += f"Total points: {submission.grade}\n"
            
            #output += f"Commit graded: {Repo(path).head.commit}"
            output += f"Graded at {str(datetime.now(est).strftime('%I:%M %p %m/%d/%Y'))}\n"
            f = open(os.path.join(path,"log.txt"), "w")
            f.write(output)
            f.close()
            cmd = f"cd {path}; rm *.zip; zip artifacts-{submission.id}.zip *.out *.txt *.diff"
            return_code, stdout_, stderr_ = run_cmd(cmd,False,10)
            if(return_code == 0):
                archive_path = os.path.join(path, f"artifacts-{submission.id}.zip")
                old_grade = get_old_grade(submission.id, project)
                print(f"{old_grade},{submission.grade},{submission.id},kghj7")
                if old_grade < submission.grade:
                    print(f"commenting on {int(submission.id)} {old_grade},{submission.grade}")
                    comment_file(API_KEY, int(submission.assignmentid),int(submission.id),archive_path)
            print(stderr_)
            #print(stdout_)
            print(return_code)
        est = pytz.timezone('US/Eastern')
        
        submission.status += "::Graded at " + str(datetime.now(est).strftime('%I:%M %p %m/%d/%Y'))
    print(f"Graded {count} submissions")

# Creates the file import for webcourses with updated student grades.
def update_grades(submissions, project, regrade=False):
    print("update grades")
    #project = "Project " + project[-1]
    no_submission = []
    comments = []

    # Creates the grade import csv for all students
    with open("students.csv", "r") as f, open("import.csv", "w") as t:
        reader = csv.DictReader(f)
        res = project in reader.fieldnames
        # print(test)
        # print([s for s in reader.fieldnames ])
        project = [s for s in reader.fieldnames if project in s][0]

        headers = ["Student", "ID", "SIS User ID", 
                    "SIS Login ID", "Section", project]

        writer = csv.DictWriter(t, fieldnames=headers)
        writer.writeheader()
        count = 0
        total = 0
        skipped = 0
        for row in reader:
            total += 1
            exist = False
            for submission in submissions:
                # if we are regrading, skip the ones that checkout to the valid git tag
                if regrade and  not submission.tag_exists: 
                    continue
                if row["ID"] in submission.id and len(row["ID"]) > 0:
                    exist = True
                    count = count + 1
                    if row[project] == "":
                        row[project] = submission.grade
                        r = {}
                        for e in headers:
                            r.update({e:row[e]})
                        writer.writerow(r)
                        comments.append(submission)
                        break
                    if float(row[project]) <= submission.grade:
                        row[project] = submission.grade
                        r = {}
                        for e in headers:
                            r.update({e:row[e]})
                        writer.writerow(r)
                        comments.append(submission)
                        break
                    else:
                        print(f"skipping {len(row['ID'])} {submission.grade} {submission.id} {row[project]} {row['ID']}")

                
            if not exist and not regrade:
                comments.append([row["Student"], row["ID"], 
                        "None", 0, "No submission."])
                row[project] = 0
                r = {}
                for e in headers:
                    r.update({e:row[e]})
                writer.writerow(r)

    # Sneaky sorting by last name
    # s = [i[0].split()[1:2] + i for i in comments if i[0] is not ""]
    # s.sort(key=lambda x: x[0])
    # s = [i[1:] for i in s]
    rows = [[s.name, s.id, s.grade, s.status] for s in submissions]
    # Creates a csv for assignment comments
    with open("comments.csv", "w") as f:
        headers = ["Student", "ID", "Grade", "Comment"]
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

# Prints updates for the grading script
def print_update(update, i, l, repository):
    print(update + " " + str(i+1) + "/" + str(l) + ": " + repository)


# Either clones the students repo or fetches the latest data and checks out
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
                submission.path = path
            else:
                if os.path.isdir(path): # check if clone worked
                    for remote in Repo(path).remotes:
                        #remote.fetch()
                        print_update("Fetching", i,
                                len(submissions), submission.repo)
                    submission.status += "\n Fetched"
                    submission.path = path
                else:
                    if not make_repo(path, submission):
                        submission.repo = None
                        failed_make_repo.append(str(submission))
                        continue
                    print_update("Cloning", i, len(submissions),submission.repo)
            if project in Repo(path).tags:
                Git(path).checkout(project)
                submission.tag_exists = True
        
        else:
            not_found.append(project + " not found.")
            submission.status += "\n repo not found"


def get_old_grade(id, project):
    # Creates the grade import csv for all students
    with open("students.csv", "r") as f:
        reader = csv.DictReader(f)
        res = project in reader.fieldnames
        # print(test)
        # print([s for s in reader.fieldnames ])
        project = [s for s in reader.fieldnames if project in s][0]
        for row in reader:
                if id in row["ID"]  and len(row["ID"]) > 0:
                    return float(row[project])





def calculate_late(date, project):
    
    est = pytz.timezone('US/Eastern')

    due = [datetime(2020, 10, 16,23 , 59, 0, 0),
            datetime(2020, 10, 30, 23, 59, 0, 0),
            datetime(2020, 11, 20, 23, 59, 0, 0),
            datetime(2020, 12, 4, 23, 59, 0, 0),
            datetime(2019, 12, 5, 23, 59, 0, 0)]

    if date - est.localize(due[project - 1]).timestamp() <= 0:

        return 0
    return 2

            
if __name__ == "__main__":
    regrade = False
    project = sys.argv[1]
    API_KEY = sys.argv[2]
    try:
        regrade = sys.argv[3]
        regrade = True
    except IndexError:
        pass

    submissions = get_submissions(6846888)
    pull_checkout(submissions, project)
    run_test_cases(submissions, project, API_KEY, regrade)
    update_grades(submissions, project,regrade)

