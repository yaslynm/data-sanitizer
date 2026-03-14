
#
# Client-side app to upload a text file containing sensitive data
# and receive a sanitization report.
# 
# Request body looks like:
#  {
#    "name": "example.txt"
#    "content": "My email is user@example.com"
#  }
#

import sys
import pathlib

sys.tracebacklimit = 0

baseurl = "https://2qjyavc9pg.execute-api.us-east-2.amazonaws.com/prod"

url = baseurl + "/process"

fielename = input("Enter filename> ")

if not pathlib.Path(filename).is_file():
    print(f"**Error: file '{fillename}' does not exist...")
    sys.exit(0)

with open(filename, "rb") as infile:
    text = infile.read()

data = {
    "name": filename,
    "content":text
}

print(f"Calling web service to sanitize '{filename}'...")

response = requests.post(url, json=data)


