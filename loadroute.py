import arrow
from dtraccar import traccar
import pandas as pd
import json
import time
import os
from pprint import pprint as pp
import warnings
warnings.filterwarnings("ignore")


T = traccar.Traccar()

if __name__ == '__main__':
    print(f'''
\033[H\033[J
*************************************************************
* Prefetch data from {T.cfg['url']} 
*************************************************************
''')

print(f"fetch route data from {T.cfg['url']}:")
t6 = time.time()
nroute = pd.read_hdf(T.cfg['prefetch_route'], "data").to_dict(orient='records')
t7 = time.time()
print(f"route : {len(nroute)} recs loaded from {T.cfg['prefetch_route']} in {t7-t6:.2f} seconds.\n")

d = arrow.get(nroute[-1]['fixTime']).format('YYYY-MM-DDTHH:mm:ss') + 'Z'
#print(nroute[-1]['fixTime'], d)  

print(f"fetch route data from {T.cfg['url']}")
t2 = time.time()
route = T.getRouteData(startdate=d)
t3 = time.time()
print(f"route : {len(route)} recs fetched  in {t3-t2:.2f} seconds.\n")

last_id = nroute[-1]['id']
print(f"last id in prefetch route: {last_id}")
print(f"last id in new route fetch: {route[-1]['id']}")

n = (route[-1]['id']) - last_id

ns = len(route) - n
print(f"new route records start here: {route[ns]['id']}")

if n > 0:
  for i in range(n):
    print(i, route[ns + i]['id'])

pp(route[-3:])