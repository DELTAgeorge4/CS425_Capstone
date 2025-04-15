import vt


f = open("/home/API_KEY/api_key.txt", "r")
# Read the API key from the file
API_KEY = f.read().strip()
# Close the file
f.close()

# print(API_KEY)

client = vt.Client(API_KEY)

with open("/home/API_KEY/api_key.txt", "rb") as f:
  analysis = client.scan_file(f, wait_for_completion=True)