from dtraccar import traccar

T = traccar.Traccar()

if __name__ == '__main__':
    print(f'''
\033[H\033[J
*************************************************************
* Prefetch data from {T.cfg['url']} 
*************************************************************
''')
    
    def _prefetch(self):
        prefetch = {}
        prefetch['fetchdate'] = arrow.now().format('YYYY-MM-DDTHH:mm:ss') + 'Z'
        print(f"fetchdate: {prefetch['fetchdate']}")
        prefetch['devices'] = self.getDevices()
        print(f"devices: {len(prefetch['devices'])}")
        prefetch['events'] = self.getEvents()
        print(f"events: {len(prefetch['events'])}")
        prefetch['route'] = self.getRouteData()
        print(f"route: {len(prefetch['route'])}")
        with open('prefetch.json', mode="w") as fp:
            json.dump(prefetch, fp, indent=4)
        print("prefetch.json written.")
traccar.T._prefetch()


