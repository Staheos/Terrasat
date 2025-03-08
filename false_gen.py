import hashlib
import json
import datetime
import random

data_list = []

for i in range(0, 10000):
    hasz = hashlib.sha512(f'Kocham Weronikę ❤️❤️\nGood luch, Terrasat. SAODPA (Imiona) GENERATION_ID: {i} Będzie dobrze!'.encode()).hexdigest()
    data = {
        "time": datetime.datetime.now().timestamp() - 60 * 60 * 24 * 17 + i / 10 + (random.randint(0, 1000) - 500) / 1000,
        "id:": i,
        "type": "test",
        "data": hasz
        }
    data_list.append(json.dumps(data))

print(data_list)
open("testing_data.txt", "w").write("\n".join(data_list))