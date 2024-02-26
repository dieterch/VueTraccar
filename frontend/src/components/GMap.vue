<script setup>
import { ref } from "vue";
import { GoogleMap, MarkerCluster, Marker, Polyline, InfoWindow } from "vue3-google-map";
import { GoogleMapsLink } from "@/tools"
import { polygone, center, zoom, locations, togglemarkers, togglepath, getMDDocument } from '@/app';
import { maps_api_key } from '@/secret';
import MarkdownViewDialog from "./MarkdownViewDialog.vue";
import MarkdownEditDialog from "./MarkdownEditDialog.vue";

// const center = ref({ lat: 47.389207790740315, lng: 11.774475611608988 });
const flightPath = ref({
    path: polygone.value,
    geodesic: true,
    strokeColor: "#FF0000",
    strokeOpacity: 1.0,
    strokeWeight: 2
  });

function closeInfoWindows() {
    console.log('closeInfoWindows()');
    locations.value.forEach((location) => {
        location.infowindow = false;
    });
}

const markdownviewdialog = ref(false)
const markdowneditdialog = ref(false)
const mode = ref('light')
const content = ref(`## Markdown Basic Syntax

I just love **bold text**. Italicized text is the _cat's meow_. At the command prompt, type "nano".

My favorite markdown editor is [vue3-markdown](https://www.npmjs.com/package/vue3-markdown).

1. First item
2. Second item
3. Third item

> Dorothy followed her through many of the beautiful rooms in her castle.

## GFM Extended Syntax

Automatic URL Linking: https://www.npmjs.com/package/vue3-markdown

~~The world is flat.~~ We now know that the world is round.

- [x] Write the press release
- [ ] Update the website
- [ ] Contact the media

| Syntax    | Description |
| --------- | ----------- |
| Header    | Title       |
| Paragraph | Text        |`);

const ncontent = ref('## nothing.')
async function openviewdialog(key) {
    console.log('openviewdialog', key)
    const doc = await getMDDocument(key)
    console.log('openviewdialog', doc)
    ncontent.value = doc
    markdownviewdialog.value = true
}

</script>

<template>
  <GoogleMap
    :api-key="maps_api_key" 
    style="width: 100%; height: calc(100vh - 48px);" 
    :center="center" 
    :zoom="zoom" 
    @click="closeInfoWindows">
    <Polyline v-if="togglepath" :options="flightPath" />
    <MarkerCluster 
      v-if="togglemarkers"
    >
        <Marker
          v-for="(location, i) in locations"
          :key="i"
          :options="{ position: location }"
          @click="closeInfoWindows"
        >
        <!--InfoWindow :options="{ position: location, content: 'Hello World!' }" /-->
        <InfoWindow 
          :options="{ position: location, minWidth: 250}"
          v-model="location.infowindow"
        >
          <div id="content">
              <div id="siteNotice">
              </div>
              <!--h1 id="firstHeading" class="firstHeading">{{ location.country }} ({{ location.period }}h)</h1-->
              <h2>{{ location.address.split(',')[0] }}</h2>
              <div id="bodyContent">
                <h4
                  v-for="(line, i) in location.address.split(',').slice(1)"
                >
                  {{ line }}
                </h4>
                <table
                  style="width: 100%; text-align: left; margin-top: 5px;"
                >
                  <tr>
                    <th>Lat, Lng </th>
                    <td>{{ location.lat.toFixed(2) }}, {{ location.lng.toFixed(2) }}</td>
                  </tr>
                  <tr>
                    <th>von</th>
                    <td>{{ location.von }}</td>
                  </tr>
                  <tr>
                    <th>bis</th>
                    <td>{{ location.bis }}</td>
                  </tr>
                  <tr>
                    <th>Dauer</th>
                    <td>{{ location.period }}h</td>
                  </tr>
                </table>
                <p> 
                  <a 
                  target="_blank" 
                  :href="GoogleMapsLink(location.lat, location.lng)">
                  Link zu Google Maps</a>
                </p>
                <v-btn
                  color="primary"
                  class="ma-2"
                  size="x-small"
                  @click="openviewdialog(location.key)"
                >
                  Beschreibung
                </v-btn>
                <v-btn
                  color="tertiary"
                  class="ma-2"
                  size="x-small"
                  @click="markdowneditdialog = true"
                >
                  Beschreibung editieren
                </v-btn>
              </div>
          </div>
        </InfoWindow>
        </Marker>
    </MarkerCluster>
    <MarkdownViewDialog 
      :content="ncontent"
      :mode="mode"
      :key="markdownviewdialog"
      :dialog="markdownviewdialog"
      @getMarkDownDialog="(e)=>{markdownviewdialog = e}" />
    <MarkdownEditDialog
      :dialog="markdowneditdialog"
      :key="markdowneditdialog" 
      @getMarkDownEditDialog="(e)=>{markdowneditdialog = e}"
      @getContent="(e)=>{console.log(e)}"
    />
  </GoogleMap>
</template>