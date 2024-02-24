<script setup>
import { ref } from 'vue'
import { tracdate } from '@/tools';
import { 
  startdate, stopdate, 
  polygone, 
  togglemap, 
  travel, 
  travels, 
  toggletravels,
  route, 
  toggleroute,
  events,
  toggleEvents
} from '@/app';

</script>

<template>
  <v-app class="rounded rounded-md">
    <AppBar />
    <!--SideBar /-->
    <!--v-main class="d-flex align-center justify-center" style="min-height: 300px;"-->
    <v-main>
        <DebugDialog />
        <GMap v-if="togglemap" :key=polygone />
        <pre v-if="toggletravels">
Reise {{ travel }}
        </pre>
        <pre v-if="toggleroute">
Route {{ route }}
        </pre>
        <pre v-if="toggleEvents">
Events {{ events }}
        </pre>
      </v-main>
  </v-app>
</template>