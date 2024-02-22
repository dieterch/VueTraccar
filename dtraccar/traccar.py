import arrow
import math
import os
import requests
from statistics import mean
from pprint import pprint as pp, pformat as pf
from . import kml
import tomli as tml
import googlemaps

############################## Class Interface ##############################
   
class Traccar:
    def __init__(self, cfgfile='config.toml'):
        with open(cfgfile, mode="rb") as fp:
            self._cfg = tml.load(fp)
        self.gmaps = googlemaps.Client(key=self._cfg['mapsapikey'])
            
    @property
    def cfg(self):
        return self._cfg
    
    def _cfghelp(self, cfg):
        if cfg is None:
            cfg = self._cfg
        return cfg
    
    # export function traccar_payload() {
    # return {
    #     'name': travel.value.title || 'filename',
    #     'device': device.value.id,
    #     'startdate': tracdate(startdate.value),
    #     'enddate': tracdate(stopdate.value),
    #     'maxpoints': '2500'
    # }
    # }
    
    # def _kmlpar(self, req):
    #     #{'device': 4,
    #     #'enddate': '2023-09-02T00:00:00Z',
    #     #'maxpoints': '2500',
    #     #'name': '2023-08-10 (22 Tage)',
    #     #'startdate': '2023-08-10T00:00:00Z'}
    #     if req is None:
    #         par = { 'name': self._cfg['kmlname'],
    #                 'maxpoints': self._cfg['maxpoints'],
    #                 'device': self._cfg['devid'],
    #                 }
    #     else:
    #         par = req
    #     return par
    
    def _traccar_payload(self, req, device=None, startdate = None, enddate=None, tname=None, maxpoints=None):
        if req is None:
            lstartdate = startdate if startdate is not None else self._cfg['startdate']
            lenddate = enddate if enddate is not None else arrow.now().format('YYYY-MM-DDTHH:mm:ss') + 'Z'
            lnamedate = f"{arrow.get(lstartdate).format('YYYY-MM-DD')} ({(arrow.get(lenddate)-arrow.get(lstartdate)).days} Tage)"
            req = { 
                'deviceId': device if device is not None else self._cfg['devid'],
                'from': lstartdate, 
                'to': lenddate,
                'name': tname if tname is not None else lnamedate,
                'maxpoints': maxpoints if maxpoints is not None else self._cfg['maxpoints']
            }
        return req
    
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
                params=self._traccar_payload(req),
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
                    ab = arrow.get(ev['serverTime']).shift(hours=-self._cfg['standperiod'])
                    ab_ev = ev

                if intravel:
                    if ev['type'] == 'geofenceEnter':  # Rückkehr aus dem Urlaub
                        an = arrow.get(ev['serverTime']).shift(hours=self._cfg['standperiod'])
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
                                'device': req['deviceId'] if req is not None else cfg['devid']
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
                params=self._traccar_payload(req),
                timeout=100.000)
            r.raise_for_status()
            if hasattr(self, '_route'):
                del self._route
            # filter out very long distances
            self._route = [p for p in r.json() if p['attributes']['distance'] < 1000000.0]
            #self._route = r.json()
            print(f"route: {len(r.json()) - len(self._route)} Punkte gefiltert.")
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)

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

    def plot(self, cfg=None, req=None):
        cfg = self._cfghelp(cfg)
        self.getRouteData(cfg, req)
        bounds = self._bounds(self._route)
        total_dist, stand_periods = self._analyzeroute(self._route)
        print(f"centerlat: {self._center(bounds)['lat']:.1f}, centerlng: {self._center(bounds)['lng']:.1f}")
        plotdata = [{"lat": d['latitude'], "lng": d['longitude']} for d in self._route]
        #pp(stand_periods[:5])
        return {
            "bounds": bounds,
            "center": self._center(bounds),
            "zoom": self._zoom(bounds),
            "distance": f"{total_dist:.0f} km",
            "markers": self._clean_stand_periods(stand_periods),
            "plotdata": plotdata
        }

                
    def kml(self, cfg=None, req=None):
        cfg = self._cfghelp(cfg)
        #print("in T.kml vor _traccar_payload:")
        #pp(req)
        req = self._traccar_payload(req)
        #print("in T.kml nach _traccar_payload:")
        #pp(req)
        self.getRouteData(cfg, req)
        data = self._route
        kmldata = kml.tokml(data)
        file_name = req['name'] + '.kml' if req is not None else 'route.kml'
        file_path = os.getcwd() + "/dist/static/"
        full_path = file_path + file_name
        kml.writeKML(cfg, req, full_path, kmldata)
        return file_name, full_path
        
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

def plot(cfg, par):
    return T.plot(cfg, par)

def downloadkml(cfg, par):
    return T.kml(cfg, par)
