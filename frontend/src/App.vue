<template>
  <v-layout class="rounded rounded-md">
  <SideBar />
    <!-- AppBar /-->
    <v-main class="d-flex align-center justify-center" style="min-height: 300px;">
      <GMap />
      <!--pre class="mt-4">
ab: {{ startdate }}
an: {{ stopdate }}
{{ travel }}
{{ polygone }}
      </pre-->
        </v-main>
  </v-layout>
</template>

<script setup>
import { ref } from 'vue'
import { startdate, stopdate, device,  tracdate, 
  travels, travel, polygone } from '@/app';

</script>
