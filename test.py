import requests

url = "http://127.0.0.1:5000/recommend?course_title=java"
response = requests.get(url)

print("Response Status Code:", response.status_code)
print("Response JSON:", response.json())
