<template>
  <GoogleMap 
    api-key="" 
    style="width: 100%; 
    height: 500px" 
    :center="center" 
    :zoom="10">
    <Polyline :options="flightPath" />
  </GoogleMap>
</template>

<script setup>
import { ref, onBeforeMount } from "vue";
import { GoogleMap, Polyline } from "vue3-google-map";
import {  map_api_key, getMapApiKey } from '@/app';

const center = ref({ lat: 47.389207790740315, lng: 11.774475611608988 });
const flightPath = ref({
  path: [
    { lat: 47.3, lng: 11.7 },
    { lat: 47.6, lng: 11.8 },
    { lat: 47.3, lng: 12.8 },
  ],
  geodesic: true,
  strokeColor: "#FF0000",
  strokeOpacity: 1.0,
  strokeWeight: 2,
});

onBeforeMount(() => {
    getMapApiKey()
})
</script>