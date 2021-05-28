from controller import SmartAPI
import requests
# import time

def transfer_ownership(previoususer, newuser):
    response = requests.get("https://smart-api.info/api/query?q=_meta.username:{}&fields=info.title,_meta.username&size=100".format(previoususer))
    print(f"Transfering ownership from: '{previoususer}' to '{newuser}'.")
    hits = response.json()['hits']
    # print(hits)
    for item in hits:
        if item['_meta']['username'] == previoususer:
            print('found '+item['_meta']['username'])
            try:
                if item["_id"] == 'dc91716f44207d2e1287c727f281d339':
                    print('FOR ANDREW', item['info']['title'])
                    an = SmartAPI.get(item['_id'])
                    an.username = 'andrewsu'
                    res1 = an.save()
                    print(f"Changed ownership from '{previoususer}' to 'andrewsu' successfully: {res1}")
                else:
                    ch = SmartAPI.get(item['_id'])
                    ch.username = newuser
                    res2 = ch.save()
                    print(f"Changed ownership from '{previoususer}' to '{newuser}' successfully: {res2}")
            except Exception as e:
                print(f"could not get {item['_id']} because {e}")
            # time.sleep(2)

if __name__ == '__main__':
    transfer_ownership('kevinxin90', 'newgene')