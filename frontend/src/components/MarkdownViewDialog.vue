<script setup>
import { ref, defineEmits, defineProps } from 'vue'
// import { markdownviewdialog  } from '@/app';
import { VMarkdownView } from 'vue3-markdown'
import 'vue3-markdown/dist/style.css'

const props = defineProps({ content: String, mode: String, dialog: Boolean})
const emit = defineEmits(['getMarkDownDialog'])

const ldialog = ref(props.dialog)
// console.log('ldialog', ldialog.value)

const update = () => {
    // console.log('update', ldialog.value)
    emit('getMarkDownDialog', ldialog.value);
}

</script>

<template>
    <v-dialog
        v-model="ldialog"
        width="auto"
        >
        <v-card>
        <v-card-title>
            Markdown Viewer
        </v-card-title>
        <v-card-text>
        <VMarkdownView
            :mode="mode"
            :content="content"
            @update:model-value="update"
        ></VMarkdownView>
        </v-card-text>
        <v-card-actions>
            <v-btn
            color="primary"
            variant="text"
            @click="ldialog = false; update()"
            >
            Close
            </v-btn>
        </v-card-actions>
        </v-card>
    </v-dialog>
</template>
