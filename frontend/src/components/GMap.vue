<script setup>
import { ref } from "vue";
import { GoogleMap, Polyline } from "vue3-google-map";
import { polygone, center, zoom } from '@/app';
import { maps_api_key } from '@/secret';

// const center = ref({ lat: 47.389207790740315, lng: 11.774475611608988 });
const flightPath = ref({
    path: polygone.value,
    geodesic: true,
    strokeColor: "#FF0000",
    strokeOpacity: 1.0,
    strokeWeight: 2,
  });

</script>

<template>
  <GoogleMap
    :api-key="maps_api_key" 
    style="width: 100%; height: 100vh;" 
    :center="center" 
    :zoom="zoom">
    <Polyline
      :options="flightPath" />
  </GoogleMap>
</template>