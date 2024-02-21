<script setup>
import { mergeProps } from 'vue';
import { startdate, stopdate, travel, travels, 
    distance, getTravels, getPolygone } from '@/app';

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
    <v-app-bar
        name="menu-bar" 
        density="standard"
        color="grey-darken-3"
        :elevation="0"
        flat
        >
        <template v-slot:prepend>
            <v-menu location="bottom">
                <template v-slot:activator="{ props: menu }">
                    <v-tooltip open-delay="500">
                        <template v-slot:activator="{ props: tooltip }">
                            <v-app-bar-nav-icon
                            v-bind="mergeProps(menu, tooltip)"
                            nosize="small"
                            >
                            </v-app-bar-nav-icon>
                        </template>
                        <span>Tooltip</span>
                    </v-tooltip>
                </template>
                <v-list density="compact">
                    <v-list-item>
                        <v-list-item-title>Item 1</v-list-item-title>
                        <v-list-item-title>Item 2</v-list-item-title>
                        <v-list-item-title>Export as KML</v-list-item-title>
                    </v-list-item>
                </v-list>
            </v-menu>
            <!--v-app-bar-title class="ml-2">Traccar Viewer</v-app-bar-title-->
        </template>

        <template v-slot:default>
            <v-select
                :label="`${travels.length} Reisen`"
                flat
                density="compact"
                prepend-icon="mdi-rv-truck"
                v-model="travel"
                :items="travels"
                @update:model-value="update_travel"
                class="mt-5 ml-6 mb-0 pb-0"
            ></v-select>
        </template>
        <template v-slot:append>
            <v-chip variant="flat" color="transparent">
                {{ distance }}
            </v-chip>
            <DateDialog :key="startdate" :datum="startdate" @getDate="setStartDate"/>
            <DateDialog :key="startdate" :datum="stopdate" @getDate="setStopDate"/>
            <!--v-switch
                v-model="order"
                hide-details
                inset
                label="Toggle order"
                true-value="-1"
                false-value="0"
            ></v-switch-->
        </template>
    </v-app-bar>
</template>
