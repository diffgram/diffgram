<template>
    <v-card elevation="0">
    <v-container>
        <v-layout column>

        <v-card-title>
            Update Dataset
        </v-card-title>

        <v-text-field 
            v-if="current_directory"
            v-model="current_directory.nickname"
            label="Name"
        />

        <v-btn 
            color="primary"
            :loading="loading"
            :disabled="loading"
            @click="on_dataset_update('RENAME')"
        >
            Rename
        </v-btn>

        <v-btn 
            color="warning"
            :loading="loading"
            :disabled="loading"
            @click="on_dataset_update('ARCHIVE')"
        >
            Archive
        </v-btn>

        <v_error_multiple :error="error" />

        <v-alert 
            v-if="show_success"
            type="success"
        >
            Success
        </v-alert>
        </v-layout>
    </v-container>

    </v-card>
</template>

<script lang="ts">
import Vue from "vue";
import v_error_multiple from "../../regular/error_multiple.vue"
import { update_dataset } from '../../../services/datasetServices';

export default Vue.extend( {
  name: 'directory_update',
  props: {
    project_string_id: {
        type: String,
        required: true
    },
    current_directory_prop: {
        type: Object,
        required: true
    }
  },
  components: {
    v_error_multiple
  },
  data() {
    return {
        mode: "RENAME" as string,
        loading: false as boolean,
        show_success: false as boolean,
        error: {} as object,
        current_directory: undefined as object
    }
  },
  watch: {
    current_directory_prop: function() {
        this.current_directory = this.current_directory_prop
    }
  },
  mounted() {
    this.current_directory = this.current_directory_prop
  },
  methods: {
    on_dataset_update: async function (mode: string): Promise<void> {
        this.mode = mode
        this.loading = true
        this.error = {}
        this.show_success = false

        const [success, error] = await update_dataset(this.project_string_id, this.current_directory_prop, this.mode)

        if (!error) {
            this.show_success = true
            this.$emit('directory_updated', success.updated_director, this.mode)
        } else {
            // this.$route_api_errors(error)
        }
        this.loading = false
    }
  }
}
) 
</script>
