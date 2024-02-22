<script setup>
import { ref } from 'vue'
import { tracdate } from '@/tools';
import { 
  startdate, stopdate, 
  travel, travels, 
  route, 
  polygone, 
  togglemap, 
  toggletravels,
  toggleroute
} from '@/app';
import SettingsDialog from './components/SettingsDialog.vue';

</script>

<template>
  <v-app class="rounded rounded-md">
    <AppBar />
    <!--SideBar /-->
    <!--v-main class="d-flex align-center justify-center" style="min-height: 300px;"-->
    <v-main>
        <SettingsDialog />
        <GMap v-if="togglemap" :key=polygone />
        <pre v-if="toggletravels">
Reise {{ travel }}
        </pre>
        <pre v-if="toggleroute">
Route {{ route }}
        </pre>
      </v-main>
  </v-app>
</template>