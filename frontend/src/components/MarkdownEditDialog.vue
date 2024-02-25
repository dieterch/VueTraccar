<script setup>
import { ref } from 'vue'
import { VMarkdownEditor } from 'vue3-markdown'
import { markdowneditdialog  } from '@/app';
import 'vue3-markdown/dist/style.css'

const content = ref('')
const handleUpload = (file) => {
  console.log(file)
  return 'https://i.postimg.cc/52qCzTVw/pngwing-com.png'
}
</script>

<template>
    <v-dialog
        v-model="markdowneditdialog"
        width="auto"
        >
        <v-card>
        <v-card-title>
            Markdown Editor
        </v-card-title>
        <v-card-text>
            <VMarkdownEditor
                v-model="content"
                locale="en"
                :upload-action="handleUpload"
            />
        </v-card-text>
        <v-card-actions>
            <v-btn
            color="primary"
            variant="text"
            @click="markdowneditdialog = false"
            >
            Close
            </v-btn>
        </v-card-actions>
        </v-card>
    </v-dialog>
</template>
