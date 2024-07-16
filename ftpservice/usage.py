import requests

def upload_file(file_path, upload_url):
    with open(file_path, "rb") as file:
        response = requests.post(upload_url, files={"file": file})
    return response.json()

if __name__ == "__main__":
    file_path = r"S:\MyProjects\IssueTracker\webservice\uploads\19083322da77d879.html"
    upload_url = "http://localhost:8080/upload/"
    response = upload_file(file_path, upload_url)
    print(f"File uploaded to {response['file_url']}")
