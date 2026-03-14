
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
# Authors:
#   Kai'lyn Mohammed
#   Reem Khalid
#   Yas'lyn Mohammed
#

import sys
import pathlib
import boto3
import data_sanitizer


sys.tracebacklimit = 0

print()
print("**starting**")
print()

print("**initalize**")
success = data_sanitizer.initialize('data_sanitizer-config.ini', 'sanitizerfull')
print(success)

print()

print("**get_ping**")
M = data_sanitizer.get_ping()
print(f"M: {M}")

print("**post_file:")
filename = "test.txt"
done = data_sanitizer.post_file(filename)
print(f"uploaded {filename}")

print()
print("**Done**")
print()

# baseurl = "https://2qjyavc9pg.execute-api.us-east-2.amazonaws.com/prod"

# url = baseurl + "/process"

# fielename = input("Enter filename> ")

# if not pathlib.Path(filename).is_file():
#     print(f"**Error: file '{fillename}' does not exist...")
#     sys.exit(0)

# with open(filename, "rb") as infile:
#     text = infile.read()

# data = {
#     "name": filename,
#     "content":text
# }

# print(f"Calling web service to sanitize '{filename}'...")

# response = requests.post(url, json=data)


