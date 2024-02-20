import { ref, shallowRef, computed } from 'vue'
import axios from 'axios';

export const host = ref(window.location.host)
export const protocol = ref(window.location.protocol)    
// export const devicesRec = ref([])

export const device = ref({name:'WMB Tk106', id:4})
export const startdate = ref(new Date('2019-03-01T00:00:00Z'))
export const stopdate = ref(new Date())


export function tracdate(mydate) { return mydate.toISOString().split('T')[0] + 'T00:00:00Z'}

export async function rget(api, headers = { 'Content-type': 'application/json', }) {
    const endpoint = `${protocol.value}//${host.value}${api}`
    // console.log('rpost:', endpoint, headers)
    try {
        const response = await axios.get( endpoint, 
            { headers: headers});
        return response.data
    } catch (e) {
        console.log(`${endpoint} \n` + String(e));
        alert(`${endpoint} \n` + String(e));
    }
}

export async function rpost(api, data, headers = { 'Content-type': 'application/json', }) {
    const endpoint = `${protocol.value}//${host.value}${api}`
    // console.log('rpost:', endpoint, data, headers)
    try {
        const response = await axios.post(
            endpoint, data, { headers: headers}
            );
        return response.data
    } catch (e) {
        console.log(`${endpoint} \n` + String(e));
        alert(`${endpoint} \n` + String(e));
    }
}

export function traccar_payload() {
    return {
        'name': travel.value.title || 'filename',
        'device': device.value.id,
        'startdate': tracdate(startdate.value),
        'enddate': tracdate(stopdate.value),
        'maxpoints': '2500'
    }
}

export const travels = ref([])
export const travel = ref({})
export async function getTravels() { 
    travels.value = await rpost('/travels', traccar_payload())
    travel.value = travels.value[travels.value.length - 1]
    startdate.value = new Date(travel.value.ab);
    stopdate.value = new Date(travel.value.an);
    getPolygone()
    }

export const route = ref({})
export async function getRoute() { 
    route.value = await rpost('/route',traccar_payload())
        //console.log('route:',route.value)
    }

export const events = ref({})
export async function getEvents() { 
    events.value = await rpost('/events', traccar_payload())
        //console.log('events:',events.value)
    }

    
export function download(data, filename) {
    let fileURL = window.URL.createObjectURL(new Blob([data]));
    let fURL = document.createElement('a'); 
    fURL.href = fileURL;
    fURL.setAttribute('download', filename);
    document.body.appendChild(fURL);
    fURL.click();
    document.body.removeChild(fURL);
}

export async function downloadkml() {
    let response =  await rpost('/download.kml',
        traccar_payload(),
        {'Accept': 'application/octet-stream'})
        download(response, travel.value.title + '.kml')
}

export const polygone = ref([])
export const center = ref({lat: 0, lng: 0})
export const zoom = ref(10)
export const distance = ref('____ km')
export const locations = ref([])
// export const bounds = computed(() => {
//     let lat = polygone.value.map(p => p.lat)
//     let lng = polygone.value.map(p => p.lng)
//     return {
//         sw: {lat: Math.min(...lat), lng: Math.min(...lng)},
//         ne: {lat: Math.max(...lat), lng: Math.max(...lng)}
//     }
// })
export async function getPolygone() {
    const data = await rpost('/plotmaps', traccar_payload())
    console.log('data:', data)
    polygone.value = data['plotdata']
    zoom.value = data['zoom']
    center.value = data['center']
    distance.value = data['distance']
    locations.value = data['markers']
    // console.log('polygone:', polygone.value, 'zoom', zoom.value, 'center:', center.value)
}