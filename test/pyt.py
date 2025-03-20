import random
import time
import datetime

t = open("testing_data.txt", 'r').read()

for v in t.split('\n'):
     print(f"[{datetime.datetime.now().timestamp()}]  RECV  {v}")
     import time
     import random
     time.sleep(random.randint(0, 100) / 269)