<script setup>
import { ref, defineEmits, defineProps } from 'vue'
import { VMarkdownEditor } from 'vue3-markdown'
import 'vue3-markdown/dist/style.css'
import { MdEditor } from 'md-editor-v3';
import 'md-editor-v3/lib/style.css';



const props = defineProps({ content: String ,dialog: Boolean, file: String})
const emit = defineEmits(['getMarkDownEditDialog','getContent'])


const ldialog = ref(props.dialog)
const text = ref(props.content);
const handleUpload = (file) => {
  console.log(file)
  return 'https://i.postimg.cc/52qCzTVw/pngwing-com.png'
}

const update_dialog = () => {
    // console.log('update', ldialog.value)
    emit('getMDEditDialog', ldialog.value);
}
const update_content = () => {
    // console.log('update', ldialog.value)
    emit('getMDEditDialog', ldialog.value);
    emit('getContent', {'key':props.file, 'doc': text.value});
}
</script>

<template>
    <v-dialog
        v-model="ldialog"
        width="auto"
        :min-height="600"
        >
        <v-card>
        <!--v-card-title>
            Markdown Editor
        </v-card-title-->
        <v-card-text>
            <MdEditor 
            language="en-US"    
            v-model="text" 
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
            Save
            </v-btn>
        </v-card-actions>
        </v-card>
    </v-dialog>
</template>
