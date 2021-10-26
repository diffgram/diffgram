<template>
  <diffgram_select>

  </diffgram_select>
</template>

<script lang="ts">

  import axios from 'axios';

  import Vue from "vue";
  export default Vue.extend( {
    name: 'guide_selector',
    props: {
      'project_string_id': {
        default: null
      }
    },

    data() {
      return {
        guide_list: [],
      }
    },
    computed: {

    },
    mounted() {
      this.guide_list_api()

    },
    methods: {

      guide_list_api() {

        // there were some issues with how the
        // project string gets setup from the url (because the url doesn't contain the id),
        // so just use this from Store for now

        axios.post(
          '/api/v1/project/' + this.$store.state.project.current.project_string_id +
          '/guide/list', {

          'metadata': this.metadata

        }).then(response => {

          if (response.data.log.success == true) {

            this.guide_list = response.data.guide_list
            this.metadata_previous = response.data.metadata
          }

        })
          .catch(error => {
            console.error(error);
            this.loading = false

          });
      },
      
    }
  }

) </script>
