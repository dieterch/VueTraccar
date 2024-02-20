import arrow
import json
import math
import requests
from pprint import pprint as pp
import tomli as tml

############################## Class Interface ##############################
   
class Traccar:
    def __init__(self, cfgfile='config.toml'):
        with open(cfgfile, mode="rb") as fp:
            self._cfg = tml.load(fp)
            
    @property
    def cfg(self):
        return self._cfg
    
    def _cfghelp(self, cfg):
        if cfg is None:
            cfg = self._cfg
        return cfg
    
    def _param(self, req):
        if req is None:
            par = { 'deviceId': self._cfg['devid'],
                        'from': self._cfg['startdate'], 
                        'to': arrow.now().format('YYYY-MM-DDTHH:mm:ss') + 'Z'}
        else:
            par = { 'deviceId': req['device'],
                    'from': req['startdate'], 
                    'to': req['enddate']}
        return par
    
    def getDevices(self, cfg=None):
        try:
            cfg = self._cfghelp(cfg)
            r = requests.get(cfg['url'] + '/api/devices', auth=(
            cfg['user'], cfg['password']),
            timeout=100.000)
            r.raise_for_status()
            self._devices = r.json()
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)

    # Events
    def getEvents(self, cfg= None, req=None):
        try:
            cfg = self._cfghelp(cfg)
            r = requests.get(
                cfg['url'] + '/api/reports/events', 
                auth=(cfg['user'], cfg['password']), 
                params=self._param(req),
                timeout=100.000)
            r.raise_for_status()
            self._events = r.json()
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err) 

    # Travels
    def getTravels(self, cfg=None, req=None):
        cfg = self._cfghelp(cfg)
        if not hasattr(self, '_events'):
            self.getEvents(cfg, req)
        dres = [rec for rec in self._events if (
            rec['type'] == "geofenceEnter" or rec['type'] == "geofenceExit")]  # auf geofece events filtern
        travels = []
        
        intravel = False
        for ev in dres:
            if ev['geofenceId'] == 1:  # 1 Stellplatz Fiecht
                if ev['type'] == 'geofenceExit':  # abfahrt in den Urlaub
                    intravel = True
                    ab = arrow.get(ev['serverTime'])
                    ab_ev = ev

                if intravel:
                    if ev['type'] == 'geofenceEnter':  # Rückkehr aus dem Urlaub
                        an = arrow.get(ev['serverTime'])
                        an_ev = ev
                        # print(f"ab: {ab}, an: {an}")
                        # nur wenn die Reise länger als 2 Tage und kürzer als 170 Tage ist ...
                        if ((an-ab).days > 2) & ((an-ab).days < 170):
                            travels.append({
                                'title': f"{ab.format('YYYY-MM-DD')} ({(an-ab).days} Tage)",
                                'ab': ab.format('YYYY-MM-DDTHH:mm:ss') + 'Z',
                                'ab_ev': ab_ev,
                                'an': an.format('YYYY-MM-DDTHH:mm:ss') + 'Z',
                                'an_ev': an_ev,
                                'tage': (an - ab).days,
                                'device': req['device'] if req is not None else cfg['devid']
                            })
                        intravel = False
        self._travels = travels
 
    # Routes
    def getRouteData(self, cfg=None, req=None):
        cfg = self._cfghelp(cfg)
        try:
            r = requests.get(
                cfg['url'] + '/api/reports/route', 
                auth=(cfg['user'], cfg['password']), 
                headers={"Accept": "application/json; charset=utf-8"},
                params=self._param(req),
                timeout=100.000)
            r.raise_for_status()
            if hasattr(self, '_route'):
                del self._route
            self._route = r.json()
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)


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

    def _totaldistance(self, route):
        total = 0
        for i in range(len(route)-1):
            total += self._distance(route[i],route[i+1])
        return total

    def _bounds(self, route):
        return {
            'south': min([d['latitude'] for d in route]),
            'north': max([d['latitude'] for d in route]),
            'east': min([d['longitude'] for d in route]),
            'west': max([d['longitude'] for d in route])
        }

    def _center(self, bounds):    
        return {
            'lat': (bounds['south'] + bounds['north']) / 2,
            'lng': (bounds['east'] + bounds['west']) / 2
        }

    def _zoom(self,bounds):
        deltalat = bounds['north'] - bounds['south']
        deltalng = bounds['west'] - bounds['east']
        ext = math.sqrt(deltalat**2 + deltalng**2)
        zoom = round(0.0347*(ext**2)-0.855*ext+10.838)
        print(f"dimension: {ext:.1f}, zoom: {zoom}")
        return zoom

    def plot(self, cfg=None, req=None):
        cfg = self._cfghelp(cfg)
        self.getRouteData(cfg, req)
        bounds = self._bounds(self._route)
        print(f"centerlat: {self._center(bounds)['lat']:.1f}, centerlng: {self._center(bounds)['lng']:.1f}")
        plotdata = [{"lat": d['latitude'], "lng": d['longitude']} for d in self._route]
        return {
            "bounds": bounds,
            "center": self._center(bounds),
            "zoom": self._zoom(bounds),
            "distance": f"{self._totaldistance(self._route):.0f} km",
            "plotdata": plotdata
        }
        
############################# maintain functional interface #################
T = Traccar()
def getDevices(cfg):
    T.getDevices(cfg)
    return T._devices

def getEvents(cfg, par):
    T.getEvents(cfg, par)
    return T._events

def getTravels(cfg, par):
    T.getTravels(cfg, par)
    return T._travels

def getData(cfg, par):
    T.getRouteData(cfg, par)
    return T._route

def plotmaps(cfg, par):
    return T.plot(cfg, par)
