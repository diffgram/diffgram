<template>

  <v-dialog v-model="is_open" id="input_payload" :click:outside="close" width="1200px">
    <v-card elevation="1" v-if="selected_input">
      <v-card-title>Compound File: <span class="ml-2 secondary--text">{{selected_input.original_filename}}</span></v-card-title>
      <v-card-text>
          <input_view
            v-if="selected_input"
            title="Associated Files"
            :show_filters="false"
            :show_status_filter="false"
            :project_string_id="project_string_id"
            :compound_file_id="selected_input.file_id">

          </input_view>
      </v-card-text>
    </v-card>
  </v-dialog>

</template>

<script lang="ts">
import Vue from "vue";
export default Vue.extend({

    name: 'input_compound_dialog',
    components: {
      input_view: () => import('./input_view.vue'),
    },
    props: ['project_string_id', 'selected_input'],

    mounted() {

    },

    data() {
      return {
        loading: false,
        is_open: false,
        input: undefined
      }
    },
    watch: {

    },
    filters: {
      pretty: function (value) {
        return JSON.stringify(JSON.parse(value), null, 2);
      }
    },
    methods: {
      close() {
        this.input = undefined;
        this.is_open = false;
        this.$emit('close')
      },
      open() {
        this.is_open = true;
      },
    }
  }
) </script>


<style>
  code{
    width: 100%;
    height: 100% !important;
  }
</style>
