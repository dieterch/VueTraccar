<script setup>
import { ref, defineEmits, defineProps } from 'vue'
// import { markdownviewdialog  } from '@/app';
//import { VMarkdownView } from 'vue3-markdown'
//import 'vue3-markdown/dist/style.css'
import { MdPreview, MdCatalog } from 'md-editor-v3';
import 'md-editor-v3/lib/preview.css';


const props = defineProps({ content: String, mode: String, dialog: Boolean})
const emit = defineEmits(['getMDViewDialog'])

const ldialog = ref(props.dialog)
// console.log('ldialog', ldialog.value)

const update = () => {
    // console.log('update', ldialog.value)
    emit('getMDViewDialog', ldialog.value);
}

const id = 'preview-only';
const text = ref(props.content);
const scrollElement = document.documentElement;

</script>

<template>
    <v-dialog
        v-model="ldialog"
        width="auto"
        >
        <v-card>
        <!--v-card-title>
            Markdown Viewer
        </v-card-title-->
        <v-card-text>
        <!--VMarkdownView
            :mode="mode"
            :content="content"
            @update:model-value="update"
        ></VMarkdownView-->
        <MdPreview
            language="en-US"
            :editorId="id" 
            :text="content"
            :modelValue="content"
            v-model="text"
        />
        <!--MdCatalog 
            :editorId="id" 
            :scrollElement="scrollElement" 
        /-->
        </v-card-text>
        <v-card-actions>
            <v-btn
            color="primary"
            variant="text"
            @click="ldialog = false; update()"
            >
            Schliessen
            </v-btn>
        </v-card-actions>
        </v-card>
    </v-dialog>
</template>
