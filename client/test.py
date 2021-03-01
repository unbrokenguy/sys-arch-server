from server_api import ServerApi
import json

s = ServerApi("http://127.0.0.1:8000")

a = json.loads(s.get_category_data(1).text)

for b in a:
    print(b)
