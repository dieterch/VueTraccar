<script setup>
import { ref, watch } from "vue";
import { GoogleMap, MarkerCluster, Marker, CustomMarker, Polyline, InfoWindow } from "vue3-google-map";
import { polygone, center, zoom, locations } from '@/app';
import { maps_api_key } from '@/secret';

// const center = ref({ lat: 47.389207790740315, lng: 11.774475611608988 });
const flightPath = ref({
    path: polygone.value,
    geodesic: true,
    strokeColor: "#FF0000",
    strokeOpacity: 1.0,
    strokeWeight: 2,
  });

const infowindow = ref(false); // Will be open when mounted

watch(infowindow, (v) => {
  //alert('infowindow has been ' + (v ? 'opened' : 'closed'));
});

</script>

<template>
  <GoogleMap
    :api-key="maps_api_key" 
    style="width: 100%; height: 100vh;" 
    :center="center" 
    :zoom="zoom">
    <Polyline :options="flightPath" />
    <MarkerCluster>
        <Marker
          v-for="(location, i) in locations"
          :key="i"
          :options="{ position: location }"
        >
          <InfoWindow v-model="infowindow">
            <div id="content">{{ location.period }} h</div>
          </InfoWindow>
        </Marker>
        <!--CustomMarker
          v-for="(location, i) in locations"
          :key="i"
          :options="{ position: location, anchorPoint: 'BOTTOM_CENTER' }">
          <div style="text-align: center">
            <div style="font-size: 1.125rem">{{ location.period }} h</div>
            <img src="../../../dist/ziel.png"   width="50" height="50" style="margin-top: 8px" />
          </div>
        </CustomMarker-->
    </MarkerCluster>
  </GoogleMap>
</template>