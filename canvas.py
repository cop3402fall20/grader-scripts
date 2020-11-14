# Import the Canvas class
from canvasapi import Canvas

# Canvas API URL


# Initialize a new Canvas object

def comment_file(API_KEY, assignment, userid,filepath):
    canvas = Canvas(API_URL, API_KEY)


    course = canvas.get_course(1364800)

    assignment = course.get_assignment(assignment)

    submission = assignment.get_submission(user = userid)
    submission.upload_comment(file=filepath)
