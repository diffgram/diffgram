<template>
    <h1>Compound file</h1>
</template>

<script lang="ts">

import Vue from "vue";
import { get_child_files } from "../../../services/fileServices";
import { File } from '../../../types/files'

export default Vue.extend({
    name: 'compound_annotation_core',
    props: {
        project_string_id: {
            type: String,
            required: true
        },
        file: {
            type: Object,
            required: true
        }
    },
    data() {
        return {
            child_file_list: null as File[]
        }
    },
    async mounted() {
        const { result, error } = await get_child_files(this.project_string_id, this.file.id)
        if (error) {
            console.log(error)
        }
        if (result) {
            this.child_file_list = result
        }
    }
})
</script>