import requests

# file size large -> need 2-3 mins to update

jsonurl = 'https://soa.tainan.gov.tw/Api/Service/Get/e8d4f9f8-5f11-4e48-9a25-1684ccce49a6'
response = requests.get(jsonurl)

with open('bucket.json', 'w', encoding='utf-8') as f:
    f.write(response.text)

print('Data Updated')

