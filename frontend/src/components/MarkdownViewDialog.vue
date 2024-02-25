<script setup>
import { ref,  } from 'vue'
import { markdownviewdialog  } from '@/app';
import { VMarkdownView } from 'vue3-markdown'
import 'vue3-markdown/dist/style.css'

defineProps({
    content: String,
    mode: String,
})


</script>

<template>
    <v-dialog
        v-model="markdownviewdialog"
        width="auto"
        >
        <v-card>
        <v-card-title>
            Mardown Viewer
        </v-card-title>
        <v-card-text>
        <VMarkdownView
            :mode="mode"
            :content="content"
        ></VMarkdownView>
        </v-card-text>
        <v-card-actions>
            <v-btn
            color="primary"
            variant="text"
            @click="markdownviewdialog = false"
            >
            Close
            </v-btn>
        </v-card-actions>
        </v-card>
    </v-dialog>
</template>
