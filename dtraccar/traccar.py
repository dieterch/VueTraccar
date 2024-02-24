import arrow
import json
import math
import os
import time
import requests
from statistics import mean
import pprint
from pprint import pprint as pp, pformat as pf
import  dtraccar
import tomli as tml, tomli_w as tmlw
import googlemaps
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

############################## Class Interface ##############################
   
class Traccar:
    def __init__(self, cfgfile='config.toml'):
        with open(cfgfile, mode="rb") as fp:
            self._cfg = tml.load(fp)
        self.gmaps = googlemaps.Client(key=self._cfg['mapsapikey'])
            
    @property
    def cfg(self):
        return self._cfg

# -------------------
# api calls & caching
# -------------------            
    def getDevices(self, cfg=None):
        try:
            cfg = self._cfghelp(cfg)
            r = requests.get(cfg['url'] + '/api/devices', auth=(
            cfg['user'], cfg['password']),
            timeout=100.000)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)

    # Events
    def getEvents(self, cfg= None, req=None):
        try:
            cfg = self._cfghelp(cfg)
            r = requests.get(
                cfg['url'] + '/api/reports/events', 
                auth=(cfg['user'], cfg['password']), 
                params=self._traccar_payload(req),
                timeout=100.000)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err) 

    # Positions
    def getPosition(self, cfg=None, id=None):
        try:
            cfg = self._cfghelp(cfg)
            r = requests.get(
                cfg['url'] + '/api/positions', 
                auth=(cfg['user'], cfg['password']), 
                headers={"Accept": "application/json; charset=utf-8"},
                params={'id': id },
                timeout=100.000)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err) 

    # prefetch route data
    def prefetchRouteData(self):
        print(f"fetch route data from {self._cfg['url']}")
        t0 = time.time()
        if hasattr(self, '_route'):
            del self._route
        self._route = self._getRouteData()
        pd.DataFrame(self._route).to_hdf(self._cfg['prefetch_route'], "data", complevel=6)
        t1 = time.time()
        print(f"route : {len(self._route)} recs fetched & stored in {t1-t0:.2f} seconds.")
        return {"records" : len(self._route), "time": t1-t0}
    
    def getRouteData(self, cfg=None, req=None, device=None, startdate = None, enddate=None):
        cfg = self._cfghelp(cfg)
        if not hasattr(self, '_route'):
            # load route data from caching file, if prefetch_route file does not exist
            # call prefectchRouteData
            if not os.path.isfile(cfg['prefetch_route']):
                print(f"prefetching file {cfg['prefetch_route']} ...")
                self.prefetchRouteData()
            self._route = pd.read_hdf(self._cfg['prefetch_route'], "data").to_dict(orient='records')
        lastid = self._route[-1]['id']; lastdate = self._formatdate(self._route[-1]['fixTime'])
        _newroute = self._getRouteData(cfg=None, req=None, device=None, startdate = lastdate, enddate=None)
        # filter out the records that are already in self._route
        newroute = [r for r in _newroute if r['id'] > lastid]
        # add the new records to the self._route
        self._route.extend(newroute)
        # filter route for the requested time period
        req = self._traccar_payload(req, device = device, startdate = startdate, enddate = enddate)
        route = [p for p in self._route if p['fixTime'] > req['from'] and p['fixTime'] < req['to']]
        return route
 
    # Routes
    def _getRouteData(self, cfg=None, req=None, device=None, startdate = None, enddate=None):
        t0 = time.time()
        cfg = self._cfghelp(cfg)
        _par = self._traccar_payload(req, device = device, startdate = startdate, enddate = enddate)
        try:
            r = requests.get(
                cfg['url'] + '/api/reports/route', 
                auth=(cfg['user'], cfg['password']), 
                headers={"Accept": "application/json; charset=utf-8"},
                params=_par,
                timeout=100.000)
            r.raise_for_status()
            # filter out very long distances
            route = [p for p in r.json() if p['attributes']['distance'] < 1000000.0]
            t1 = time.time()
            print(f"load route, device: {_par['deviceId']} from: {_par['from']}, to: {_par['to']}, {len(r.json()) - len(route)} records filtered. {t1-t0:.2f} seconds.")
            return route
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)



# -----------------
# complex functions
# -----------------

    # Travels
    def getTravels(self, cfg=None, req=None):
        cfg = self._cfghelp(cfg)
        _events = self.getEvents(cfg, req)
            
        # filter events for geofence #1 Stellplatz Fiecht Enter und Exit Events
        dres = [rec for rec in _events if (
            (rec['type'] == "geofenceEnter" or rec['type'] == "geofenceExit") and rec['geofenceId'] == 1)]  # auf geofece events filtern
        travels = []
        
        # state intravel
        intravel = False
        # loop over events
        for i, ev in enumerate(dres):
            if ev['type'] == 'geofenceExit':  # Go for a trip
                # check if multiple Events happen within cfg['event_min_gap'] seconds
                if i > 1:
                    #print(f"check event {i} from {len(dres)-1}")
                    if (arrow.get(ev['serverTime']) - arrow.get(dres[i-1]['serverTime'])).seconds < self._cfg['event_min_gap']:
                            print(f"getTravels: skip event {i}({ev['type']}) at {dres[i]['serverTime']} because it is too close to {dres[i-1]['serverTime']}")
                            continue # skip this event
                # exit for a trip detected, store in lfrom
                lfrom = arrow.get(ev['serverTime'])
                lfrom_ev = ev # for debug
                intravel = True

            if intravel:
                if ev['type'] == 'geofenceEnter':  # come back from a trip
                    # check if multiple Events happen within cfg['event_min_gap'] seconds
                    if i < len(dres)-1:
                        if (arrow.get(dres[i+1]['serverTime']) - arrow.get(ev['serverTime'])).seconds < self._cfg['event_min_gap']:
                            print(f"getTravels: skip event {i}({ev['type']}) at {dres[i]['serverTime']} because it is too close to {dres[i+1]['serverTime']}")
                            continue # skip this event
                        
                    # enter, return from a trip detected, store in lto
                    lto = arrow.get(ev['serverTime'])
                    lto_ev = ev # for debug
                    
                    # store travel if it is longer than cfg['mindays'] and shorter than cfg['maxdays']
                    if ((lto - lfrom).days > self._cfg['mindays']) & ((lto - lfrom).days < self._cfg['maxdays']):
                        travels.append({
                            'title': f"{lfrom.format('YYYY-MM-DD')} ({(lto - lfrom).days} Tage)",
                            'from': { 
                                'datetime': lfrom.format('YYYY-MM-DDTHH:mm:ss') + 'Z',
                                #'event': lfrom_ev, # for debug
                                #'position': self.getPosition(cfg, lfrom_ev['positionId'])
                            },
                            'to': {
                                'datetime': lto.format('YYYY-MM-DDTHH:mm:ss') + 'Z',
                                #'event': lto_ev, # for debug
                                #'position': self.getPosition(cfg, lto_ev['positionId']),
                                #'debug_events': [  # for debug
                                #    e for e in dres \
                                #    if ((arrow.get(e['serverTime']) > lfrom.shift(days=-2)) and 
                                #        (arrow.get(e['serverTime']) < lto.shift(days=2)) and 
                                #        (e['geofenceId'] == 1))
                                #]
                            },
                            'tage': (lto - lfrom).days, # duration in days
                            'device': req['deviceId'] if req is not None else cfg['devid']
                        })
                    intravel = False # back from travel

        return travels
 
    # Berechne die Länger der Reise, die Standzeiten und deren Adressen
    def _analyzeroute(self, route):
        total_dist = 0
        stand_periods = []
        sample_period = []
        stop = {}
        start = {}
        standstill = False
        for i in range(len(route)-1):
            d = self._distance(route[i],route[i+1])
            total_dist += d
            if d < 0.1:
                if not standstill:
                    standstill = True
                    stop = route[i]
                sample_period.append(
                    {'lat': route[i]['latitude'],
                     'lng': route[i]['longitude']})
            else:
                if standstill:
                    standstill = False
                    start = route[i]
                    period = self._timediff(stop, start)
                    if period > (self._cfg['standperiod']*3600.0):
                        plat = mean([p['lat'] for p in sample_period])
                        plng = mean([p['lng'] for p in sample_period])
                        address = self.gmaps.reverse_geocode((plat, plng))
                        stand_periods.append(
                        {   'von': ' '.join(stop['fixTime'].split('T'))[:16],
                            'bis': ' '.join(start['fixTime'].split('T'))[:16],
                            'period': round(period//360.0/10.0),
                            'country': address[0]['address_components'][-2]['long_name'], # 'country': 'Austria',
                            'address': address[0]['formatted_address'], # 'address': 'Fiecht 1, 6235 Reith im Alpbachtal, Austria
                            'lat': plat,
                            'lng': plng,
                            'infowindow': False
                        })
                        sample_period = []
                    else:
                        sample_period = []
        return total_dist, stand_periods

    # return data to plot the route
    def plot(self, cfg=None, req=None):
        cfg = self._cfghelp(cfg)
        _route = self.getRouteData(cfg, req)
        center, bounds = self._center_and_bounds(_route)
        total_dist, stand_periods = self._analyzeroute(_route)
        markers = self._clean_stand_periods(stand_periods)
        print(f"centerlat: {center['lat']:.1f}, centerlng: {center['lng']:.1f}")
        plotdata = [{"lat": d['latitude'], "lng": d['longitude']} for d in _route]
        #pp(markers)        
        #pp(stand_periods[:5])
        return {
            "bounds": bounds,
            "center": center,
            "zoom": self._zoom(bounds),
            "distance": f"{total_dist:.0f} km",
            "markers": markers,
            "plotdata": plotdata
        }

                
    def kml(self, cfg=None, req=None):
        cfg = self._cfghelp(cfg)
        #print("in T.kml vor _traccar_payload:")
        #pp(req)
        req = self._traccar_payload(req)
        #print("in T.kml nach _traccar_payload:")
        #pp(req)
        data = self.getRouteData(cfg, req)
        kmldata = dtraccar.tokml(data)
        file_name = req['name'] + '.kml' if req is not None else 'route.kml'
        file_path = os.getcwd() + "/dist/static/"
        full_path = file_path + file_name
        dtraccar.writeKML(cfg, req, full_path, kmldata)
        return file_name, full_path

# ----------------------
# local helper functions
# ---------------------- 
    
    def _cfghelp(self, cfg):
        if cfg is None:
            cfg = self._cfg
        return cfg

    def _formatdate(self, d):
        return arrow.get(d).format('YYYY-MM-DDTHH:mm:ss') + 'Z'

    def _traccar_payload(self, req, device=None, startdate = None, enddate=None, tname=None, maxpoints=None):
        if req is None:
            lstartdate = self._formatdate(startdate) if startdate is not None else self._cfg['startdate']
            lenddate = self._formatdate(enddate) if enddate is not None else self._formatdate(arrow.now())
            lnamedate = f"{arrow.get(lstartdate).format('YYYY-MM-DD')} ({(arrow.get(lenddate)-arrow.get(lstartdate)).days} Tage)"
            req = { 
                'deviceId': device if device is not None else self._cfg['devid'],
                'from': lstartdate, 
                'to': lenddate,
                'name': tname if tname is not None else lnamedate,
                'maxpoints': maxpoints if maxpoints is not None else self._cfg['maxpoints']
            }
        return req

    def _center_and_bounds(self, route):
        south = min([d['latitude'] for d in route])
        north = max([d['latitude'] for d in route])
        east = min([d['longitude'] for d in route])
        west = max([d['longitude'] for d in route])
        center = {
            'lat': (south + north) / 2,
            'lng': (east + west) / 2
        }
        bounds = {
            'nw': {'latitude': north, 'longitude': west},
            'ne': {'latitude': north, 'longitude': east},
            'se': {'latitude': south, 'longitude': east},
            'sw': {'latitude': south, 'longitude': west}
        }
        return center, bounds

    def _zoom(self,bounds):
        extx = self._distance(bounds['nw'], bounds['ne'])
        exty = self._distance(bounds['nw'], bounds['sw'])
        ext = math.sqrt(extx**2 + exty**2)
        zoom = 46.527*((ext+150)**-0.288)
        print(f"dimension: {ext:.1f},(x:{extx:.1f} y:{exty:.1f}) zoom: {zoom}")
        return zoom

    def _clean_stand_periods(self, stand_periods):
        for i in range(len(stand_periods)):
            for j in range(len(stand_periods)):
                if i != j:
                    latdiff = stand_periods[i]['lat'] - stand_periods[j]['lat']
                    lngdiff = stand_periods[i]['lng'] - stand_periods[j]['lng']
                    diff = math.sqrt(latdiff**2 + lngdiff**2)
                    if  diff < 0.005:
                        if (stand_periods[i]['period'] > 0 and stand_periods[j]['period'] > 0):
                            #print(f"combine {i}-{j}, distance: {diff:.4f}")
                            stand_periods[i]['period'] += stand_periods[j]['period']
                            stand_periods[j]['period'] = 0
        return [d for d in stand_periods if d['period'] > 0]

    def _timediff(self, pt1, pt2):
        a = arrow.get(pt1['fixTime'])
        b = arrow.get(pt2['fixTime'])
        return (b - a).total_seconds()

    def _distance(self, pt1, pt2):
        R = 6373.0
        lat1r = math.radians(pt1['latitude'])
        lon1r = math.radians(pt1['longitude'])
        lat2r = math.radians(pt2['latitude'])
        lon2r = math.radians(pt2['longitude'])
        dlon = lon2r - lon1r
        dlat = lat2r - lat1r
        a = math.sin(dlat / 2)**2 + math.cos(lat1r) * math.cos(lat2r) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        return distance
        
############################# maintain functional interface #################
# T = Traccar()
# def getDevices(cfg):
#     return T.getDevices(cfg)

# def getEvents(cfg, par):
#     return T.getEvents(cfg, par)

# def getTravels(cfg, par):
#     return T.getTravels(cfg, par)

# def getData(cfg, par):
#     return T.getRouteData(cfg, par)

# def plot(cfg, par):
#     return T.plot(cfg, par)

# def downloadkml(cfg, par):
#     return T.kml(cfg, par)

if __name__ == '__main__':
    print('Please do not call this module directly. Use the app.py instead.')