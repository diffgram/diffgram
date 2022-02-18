<template>
<div id="">
<v-layout column>

  <v-card-title>
    File Transfer
  </v-card-title>

  <v_error_multiple :error="error">
  </v_error_multiple>

  <v_info_multiple :info="info">
  </v_info_multiple>

  <v-select v-if="true"
    :items="$store.state.project.current.directory_list"
    v-model="destination_directory"
    label="Destination Dataset"
    return-object
    item-text="nickname"
    :disabled="loading"
    @change=""></v-select>

  <v-select v-if="true"
      :items="action_list"
      v-model="action"
      label="Action"
      return-object
      item-text="text"
      :disabled="loading"
      @change=""></v-select>

  <!-- Copying instances is not relevant for mirroring
      or moving file -->
  <v-checkbox v-if="action.value == 'copy'"
              label="Copy Instances"
              v-model="copy_instances">
  </v-checkbox>

  <v-btn @click="file_transfer_api"
          :loading="loading"
          :disabled="loading"
          color="primary">
    Run
  </v-btn>

  <div class="text-xs-left pt-4">
  <v-btn color="primary"
          dark
          outlined
          href="https://diffgram.readme.io/docs/moving-files"
          target="_blank">
    Help
    <v-icon right>mdi-book</v-icon>
  </v-btn>
  </div>


  <!-- TODO option to clear / create another one? -->

</v-layout>
</div>
</template>

<script lang="ts">

import axios from '../../services/customInstance';

import Vue from "vue"; export default Vue.extend( {
  name: 'transfer_files',
  props: [
    'project_string_id',
    'source_directory',
    'file_list',
    'select_from_metadata',
    'metadata_previous'
    ],

  data() {
    return {

      mode: "user", // ["user", "diffgram", "..."]


      destination_directory: null,

      action_list: [
      {
        'text': 'Move to',
        'value': 'move'
      },
      {
        'text': 'Copy to',
        'value': 'copy'
      },
      {
        'text': 'Mirror',
        'value': 'mirror'
      }
      ],

      action:       {
        'text': 'Copy to',
        'value': 'copy'
      },

      copy_instances: false,

      loading: false,
      error: {},
      info: {},
      show_success: false

    }
  },
  mounted() {
    if (!this.project_string_id) {
      this.project_string_id = this.$store.state.project.current.project_string_id
    }
  },
  computed: {

  },
  methods: {

    file_transfer_api: function () {

      this.loading = true
      this.error = {}
      this.info = {}  // reset
      this.show_success = false

      axios.post(
        '/api/v1/project/' + this.project_string_id
      + '/file/transfer',
        {
          mode: "TRANSFER",
          destination_directory_id: this.destination_directory.directory_id,
          source_directory_id: this.source_directory.directory_id,
          transfer_action: this.action.value,
          file_list: this.file_list,
          copy_instances: this.copy_instances,
          select_from_metadata: this.select_from_metadata,
          metadata_proposed: this.metadata_previous // careful name change

        }).then(response => {

          this.info = {message: response.data.log.info.message};


          if (response.data.log.success == true) {

            this.show_success = true

            this.loading = false

            this.$store.commit('init_media_refresh')


          }



        }).catch(error => {

          if (error.response.status == 400) {
            this.error = error.response.data.log.error
          }
          this.loading = false
          console.log(error)
        });

    }

  }
}
) </script>
