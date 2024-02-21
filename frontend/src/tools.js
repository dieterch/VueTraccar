import { ref } from 'vue'
import axios from 'axios';
export const host = ref(window.location.host)
export const protocol = ref(window.location.protocol)   


export function tracdate(mydate) { return mydate.toISOString().split('T')[0] + 'T00:00:00Z'}

export function DECtoDMS(dd)
{
    let vars  = dd.split('.');
    let deg   = vars[0];
    let tempma = "0."+vars[1];
    tempma = tempma * 3600;
    let min = Math.floor(tempma / 60);
    let sec = tempma - (min * 60);
    return `${deg}%C2%B0${min}'${sec}%22`;
}

export function GoogleMapsLink(lat, lng) {
    let Latdir = lat > 0 ? 'N' : 'S'; let LngDir = lng > 0 ? 'E' : 'W';
    return `https://www.google.com/maps/place/${DECtoDMS(String(Math.abs(lat)))}${Latdir}+${DECtoDMS(String(Math.abs(lng)))}${LngDir}/@${lat},${lng},12z`
}

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