<template>
  <v-layout class="rounded rounded-md">
    <AppBar />
    <SideBar />
    <v-main class="d-flex align-center justify-center" style="min-height: 300px;">
      <GMap :key=polygone />
      <pre v-if="False" class="mt-4">
ab: {{ startdate }}
an: {{ stopdate }}
{{ travel }}
{{ polygone }}
      </pre>
        </v-main>
  </v-layout>
</template>

<script setup>
import { ref } from 'vue'
import { tracdate } from '@/tools';
import { startdate, stopdate, travel, polygone } from '@/app';

</script>
