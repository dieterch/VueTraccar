<template>
  <v-app class="rounded rounded-md">
    <AppBar />
    <!--SideBar /-->
      <!--v-main class="d-flex align-center justify-center" style="min-height: 300px;"-->
      <v-main>
        <GMap :key=polygone />
      </v-main>
  </v-app>
</template>

<script setup>
import { ref } from 'vue'
import { tracdate } from '@/tools';
import { startdate, stopdate, travel, polygone } from '@/app';

</script>
