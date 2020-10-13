# grader-scripts

students.csv file: Dont commit or push it. Download the gradebook.csv by exporting through canvas. Rename to students.csv and place it here.

submissions.csv: Dont commit or push it. Download the .zip of submissions for the project from webcourses. Rename and place here.



Run: python3 grade.py 'Project 1'

For canvas.py, get an api token from this page: https://webcourses.ucf.edu/profile/settings (+ Access Token blue button, half way down)

Todo: Use canvas api to upload a comment after grading. the comment should contain the grading script output and diff files.

The submission Assignment ID is in paranthesis after the assignment name in students.csv. This needs to be parsed and saved somewhere in grade.py
The submission ids need to be fetched from the canvas api: https://canvas.instructure.com/doc/api/submissions.html#method.submissions_api.index
A method doing so needs to be added to the canvas api client in canvas.py

After those two things are done, some code in grade.py needs to iterate over the submissions array, and comment .zip file for each submission.
