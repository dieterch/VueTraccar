<template>
    <v-app-bar
        order="-1"
        color="grey-lighten-2"
        flat
        title="Vue Traccar"
        density="compact"
        >
        <!--template v-slot:append>
            <v-switch
                v-model="order"
                hide-details
                inset
                label="Toggle order"
                true-value="-1"
                false-value="0"
            ></v-switch>
        </template-->
    </v-app-bar>
  </template>


<script setup>
import { order } from '@/app';

</script>