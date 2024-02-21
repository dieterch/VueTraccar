<script setup>
import { ref } from "vue";
import { GoogleMap, MarkerCluster, Marker, Polyline, InfoWindow } from "vue3-google-map";
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
        <!--InfoWindow :options="{ position: location, content: 'Hello World!' }" /-->
        <InfoWindow 
          :options="{ position: location }"
        >
          <div id="content">
              <div id="siteNotice">
              </div>
              <h1 id="firstHeading" class="firstHeading">{{ location.country }} ({{ location.period }}h)</h1>
              <div id="bodyContent">
                <p>{{ location.address }}</p>
                <p><b>Latitude</b> {{ location.lat.toFixed(2) }}, <b>Longitude</b> {{ location.lng.toFixed(2) }}</p>
                <!--p>Attribution: Uluru, <a href="https://en.wikipedia.org/w/index.php?title=Uluru&oldid=297882194">
                "https://en.wikipedia.org/w/index.php?title=Uluru</a> "</p-->
              </div>
          </div>

        </InfoWindow>
        </Marker>
    </MarkerCluster>
  </GoogleMap>
</template>