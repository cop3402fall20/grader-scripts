import requests


class CanvasClient:
    def __init__(self, token, course):
        self.token = token
        self.course = course
    def request_upload(self, assignment, submission):
        headers = {'Authorization': f'Bearer {self.token}'}


        url = f"https://webcourses.ucf.edu/api/v1/courses/{self.course}/assignments/{assignment}/submissions/{submission}/comments/files"
        payload = {'name': 'comments.zip'}
        files = []
        response = requests.request("POST", url, headers=headers, data = payload, files = files)
        

        try:
            url = (response.json()['upload_url'])
            return url
        except KeyError:
            print(response.text.encode('utf8'))
            return None

    def upload_file(self,url, file_path, assignment, submission):

        payload = {}
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
            }
        files = [('file', open(file_path,'rb'))]
        
        response = requests.request("POST", url, data = payload, files = files)
        print(response.text.encode('utf8'))

        file_id = response.json()['id']


        payload = { 'comment': {
            'file_ids': [file_id]
        }}
        url = f'https://webcourses.ucf.edu/api/v1/courses/{self.course}/assignments/{assignment}/submissions/{submission}/'

        response = requests.request("PUT", url, headers=headers, data = payload)


client = CanvasClient("", "1364800")
url = client.request_upload("6753129", "4318554")
print(url)
if url: client.upload_file(url, "", "6753129", "4318554")
