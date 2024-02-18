<script setup>
import { ref } from 'vue'
import { startdate, stopdate, getRoute, getTravels, getPolygone,
    travels, travel, tracdate, downloadkml } from '@/app';

function setStartDate(params) { 
    startdate.value = params;
    getPolygone()
}
function setStopDate(params) { 
    stopdate.value = params;
    getPolygone()
}

async function update_travel(item) {
    var index = travels.value.map(function(e) { return e.title; }).indexOf(item);
    console.log(item, index, travels.value[index]);
    travel.value = travels.value[index]
    startdate.value = new Date(travels.value[index].ab);
    stopdate.value = new Date(travels.value[index].an);
    getPolygone()
}

getTravels()
</script>

<template>
    <v-navigation-drawer color="grey-darken-2" :width="280" permanent>
        <!--v-list-item title="VueTraccar" subtitle="Create KML Files"></v-list-item-->
        <v-select
            :label="`${travels.length} Travels`"
            flat
            density="compact"
            prepend-icon="mdi-rv-truck"
            v-model="travel"
            :items="travels"
            @update:model-value="update_travel"
            class="ma-2 mb-0 pb-0"
        ></v-select>
        <v-sheet 
            class="d-flex flex-column justify-left align-center"
            color="transparent"
            >
        <DateDialog :key="startdate" :datum="startdate" @getDate="setStartDate"/>
        <DateDialog :key="startdate" :datum="stopdate" @getDate="setStopDate"/>
            <!--v-btn
                color="transparent"
                prepend-icon="mdi-map-outline"
                @click="getPolygone"
                block
                flat
                class="d-flex">
                Plot
            </v-btn-->
            <v-btn
                color="transparent"
                prepend-icon="mdi-google-earth"
                @click="downloadkml"
                block
                flat
                class="d-flex">
                KML
            </v-btn>
            <!--v-btn
                color="transparent"
                prepend-icon="mdi-wallet-travel"
                @click="getTravels()"
                class="d-flex">
                Get Travels
            </v-btn>
            <v-btn
                color="transparent"
                prepend-icon="mdi-calendar-text-outline"
                @click="getEvents()"
                class="d-flex">
                Get Events
            </v-btn-->
        </v-sheet>
        <!--v-list-item>{{ device }}</v-list-item>
        <v-list-item link title="List Item 2"></v-list-item>
        <v-list-item link title="List Item 3"></v-list-item-->
    </v-navigation-drawer>
</template>
