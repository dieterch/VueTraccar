import json
import requests
import arrow
from pprint import pprint as pp

def getDevices(cfg):
    payload = {}
    response = requests.get(cfg['url'] + '/api/devices', auth=(
        cfg['user'], cfg['password']),
        params=payload, 
        timeout=100.000)
    if response.status_code == 200:
        dres = json.loads(response.content)
        #dres = {a['name']:a for a in res}
        return dres
    else:
        return {'response.status_code' : response.status_code}


def getData(cfg, par):
    payload = {
        'deviceId': par['device'],
        'from': par['startdate'], 
        'to': par['enddate']
        }
    myheaders = {"Accept": "application/json; charset=utf-8"}
    response = requests.get(cfg['url'] + '/api/reports/route', 
        auth=(cfg['user'], cfg['password']), 
        headers=myheaders,
        params=payload, 
        timeout=100.000)
    return response.json()


def getEvents(cfg, par):
    payload = {'deviceId': par['device'],
               'from': par['startdate'], 'to': par['enddate']}
    response = requests.get(cfg['url'] + '/api/reports/events', auth=(
        cfg['user'], cfg['password']), params=payload, timeout=100.000)
    res = response.json()
    dres = [rec for rec in res if (rec['type'] == "geofenceEnter" or rec['type'] == "geofenceExit")]
    return dres


def getTravels(cfg, par):
    payload = {'deviceId': par['device'],
               'from': par['startdate'], 'to': par['enddate']}
    response = requests.get(cfg['url'] + '/api/reports/events', auth=(
        cfg['user'], cfg['password']), params=payload, timeout=100.000)
    res = response.json()  # alle events dieses devices laden

    dres = [rec for rec in res if (
        rec['type'] == "geofenceEnter" or rec['type'] == "geofenceExit")]  # auf geofece events filtern

    travels = []
    intravel = False
    eingestellt = False
    for ev in dres:
        if ev['geofenceId'] == 1:  # 1 Stellplatz Fiecht
            if ev['type'] == 'geofenceExit':  # abfahrt in den Urlaub
                intravel = True
                ab = arrow.get(ev['serverTime'])

            if intravel:
                if ev['type'] == 'geofenceEnter':  # Rückkehr aus dem Urlaub
                    an = arrow.get(ev['serverTime'])
                    # print(f"ab: {ab}, an: {an}")
                    # nur wenn die Reise länger als 2 Tage ist ...
                    if ((an-ab).days > 2) & ((an-ab).days < 170):
                        travels.append({
                            'title': f"{ab.format('YYYY-MM-DD')} ({(an-ab).days} Tage)",
                            'ab': ab.format('YYYY-MM-DDTHH:mm:ss') + 'Z',
                            'an': an.format('YYYY-MM-DDTHH:mm:ss') + 'Z',
                            'tage': (an - ab).days,
                            'device': par['device']
                        })
                    intravel = False
    return travels
