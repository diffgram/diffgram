<template>
  <div v-cloak>

    <v-dialog v-model="is_open" max-width="1000px" id="export-dialog">
      <v-card elevation="0"
              style="min-height: 600px"
              class="pl-6 pt-6 pb-6 d-flex justify-center flex-column">
        <v-card-title>Manage Schema: <span class="ml-2 secondary--text">{{ schema.name | truncate(60) }}</span></v-card-title>
        <labels_manager_tabs
          class="ma-auto"
          style="width: 100%; min-height: 600px"
          :current_schema="schema"
          :project_string_id="project_string_id"
        ></labels_manager_tabs>
      </v-card>
    </v-dialog>

  </div>
</template>

<script lang="ts">
import labels_view from '../../components/image_annotation/labels_view'
import Vue from "vue";
import Labels_manager_tabs from "./labels_manager_tabs.vue";

export default Vue.extend({

    name: 'label_manager_dialog',
    components: {
      Labels_manager_tabs,
      labels_view: labels_view
    },
    props: ['project_string_id', 'schema'],
    filters: {
      truncate: function (value, numchars) {
        return value && value.length > numchars ? value.substring(0, numchars) + "..." : value
      },
    },
    watch: {},
    mounted() {

    },

    data() {
      return {
        is_open: false
      }
    },

    methods: {
      on_label_created: function (label) {
        this.$emit('label_created', label)
      },
      open() {
        this.is_open = true;
      }
    }
  }
) </script>
