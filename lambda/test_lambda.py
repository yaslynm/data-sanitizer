import json
import process_function

body = {
        "name": "example.txt",
        "content": "Email me at user@example.com, call me at 312-555-7890, my SSN is 123-45-6789, and my card is 4111 1111 1111 1111."
} 

event = {
    "body": json.dumps(body)
}

result = process_function.lambda_handler(event, None)

print("statusCode: ", result["statusCode"])
print("body: ")
print(json.dumps(json.loads(result["body"]), indent=2))