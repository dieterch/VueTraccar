<script setup>
import { ref, defineEmits, defineProps } from 'vue'
import { VMarkdownEditor } from 'vue3-markdown'
// import { markdowneditdialog  } from '@/app';
import 'vue3-markdown/dist/style.css'

const props = defineProps({ dialog: Boolean})
const emit = defineEmits(['getMarkDownEditDialog','getContent'])


const ldialog = ref(props.dialog)
const content = ref('')
const handleUpload = (file) => {
  console.log(file)
  return 'https://i.postimg.cc/52qCzTVw/pngwing-com.png'
}

const update_dialog = () => {
    // console.log('update', ldialog.value)
    emit('getMarkDownEditDialog', ldialog.value);
}
const update_content = () => {
    // console.log('update', ldialog.value)
    emit('getMarkDownEditDialog', ldialog.value);
    emit('getContent', content.value);
}
</script>

<template>
    <v-dialog
        v-model="ldialog"
        width="auto"
        :min-height="600"
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
                :min-height="600"
            />
        </v-card-text>
        <v-card-actions>
            <v-btn
            color="primary"
            variant="text"
            @click="ldialog = false; update_dialog()"
            >
            Close
            </v-btn>
            <v-btn
            color="primary"
            variant="text"
            @click="ldialog = false; update_content()"
            >
            Ok
            </v-btn>
        </v-card-actions>
        </v-card>
    </v-dialog>
</template>
