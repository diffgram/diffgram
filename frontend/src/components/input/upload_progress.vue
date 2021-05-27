<template>
  <v-container v-if="(!progress_percentage && percentage < 100) || (progress_percentage && progress_percentage < 100)">
    <h1>Uploading Files...</h1>
    <h3 v-if="formatted_total && formatted_uploaded && !progress_percentage">
      {{formatted_uploaded}} of {{formatted_total}}
    </h3>
    <v-progress-linear
      color="secondary"
      striped
      v-model="progress_percentage ? progress_percentage : percentage"
      height="85"
    >
    </v-progress-linear>
  </v-container>
  <v-container v-else class="d-flex align-center justify-center flex-column">
    <v-icon color="success" size="86">mdi-check</v-icon>
    <h1>Files Succesfully Uploaded</h1>
    <p class="secondary--text"><strong>Check Input Table to view Pre-processing progress.</strong></p>
    <v-btn x-large @click="close_wizard" data-cy="close_wizard_button" color="success">Close</v-btn>
  </v-container>

</template>

<script lang="ts">
  import axios from 'axios';
  import Vue from "vue";
  import {v4 as uuidv4} from 'uuid';
  import filesize from 'filesize';

  export default Vue.extend({
      name: 'upload_progress',
      components: {},
      props: {
        'total_bytes': {
          default: null
        },
        'uploaded_bytes': {
          default: null
        },
        'currently_uploading': {
          default: null
        },
        'progress_percentage': {
          default: null,
        }
      },
      data() {
        return {}
      },
      computed: {
        percentage: function(){
          if(this.$props.total_bytes === 0){ return 0}
          return Math.round((this.$props.uploaded_bytes + this.$props.currently_uploading) / this.$props.total_bytes * 100);
        },
        formatted_total: function(){
          if(this.$props.total_bytes == undefined){ return undefined}
          return filesize(this.total_bytes)
        },
        formatted_uploaded: function(){
          if(this.$props.uploaded_bytes == undefined){ return undefined}
          return filesize((this.percentage/100) * this.total_bytes)
        }
      },
      watch: {
        file_list: function (new_val, old_val) {

        }
      },
      mounted() {
      },
      created() {
      },
      beforeDestroy() {

      },
      methods: {
        close_wizard: function(){
          this.$emit('close_wizard')
        }
      }
    }
  ) </script>

