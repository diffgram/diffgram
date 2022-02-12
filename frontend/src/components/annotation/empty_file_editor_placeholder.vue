<template>
  <div v-cloak id="empty_file_editor_container">
    <div style="position: relative">
      <main_menu>
      </main_menu>
    </div>
    <div v-if="!loading" class="ma-auto d-flex align-center justify-center mt-8 flex-column"
         style="width: 100%; height: 100%">
      <v-card width="850">
        <v-card-title class="ma-auto d-flex justify-center">
          <h1 class="text--secondary text-center">{{title}}</h1>
        </v-card-title>
        <v-card-text class="ma-auto d-flex justify-center flex-column">
          <v-icon size="350">{{icon}}</v-icon>
          <h2 class="text--secondary d-flex justify-center">Please add Some files to the dataset by going to the Upload
            Section</h2>
          <v-btn v-if="show_upload" color="success" x-large @click="go_to_upload">
            Upload Files
          </v-btn>
        </v-card-text>
      </v-card>

    </div>

  </div>
</template>

<script lang="ts">

import Vue from "vue";

export default Vue.extend({

    name: 'hotkeys',
    components: {},
    props: {
      project_string_id: {
        default: null
      },
      loading: {
        default: null
      },
      title:{
        default: 'No Files in This Dataset'
      },
      message:{
        default: 'No Files in This Dataset'
      },
      icon:{
        default: 'mdi-file-question'
      },
      show_upload:{
        default: true
      }
    },
    data() {
      return {}
    },
    watch: {},
    mounted() {
    },
    computed: {},
    methods: {
      go_to_upload: function () {
        this.$router.push(`/studio/upload/${this.$store.state.project.current.project_string_id}`)
      }

    }
  }
) </script>
