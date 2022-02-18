<template>
  <div>
    <div v-if="Object.keys(error).length > 0 && integration_name === 'google_gcp'"
         class="d-flex  justify-center align-center">
      <p><strong>
        <v-icon color="warning">mdi-alert</v-icon>
        Having permission issues? Check our docs on permissions for Google clicking
        <a class="primary--text"
           target="_blank"
           href="https://diffgram.readme.io/docs/google-connection-requirements">Here</a>
      </strong></p>
    </div>
    <div v-if="Object.keys(error).length > 0 && integration_name === 'amazon_aws'"
         class="pl-8 d-flex align-center">
      <p><strong>
        <v-icon color="warning">mdi-alert</v-icon>
        Having permission issues? Check our docs on permissions for AWS clicking
        <a class="primary--text"
           target="_blank"
           href="https://diffgram.readme.io/docs/amazon-web-services-connection-requirements">Here</a>
      </strong></p>
    </div>
  </div>
</template>

<script lang="ts">


  /*  Caution, re adding new select controls
   *    expects  @change="has_changes = true"  otherwise won't "save"
   *
   *
   */

  import Vue from "vue";

  export default Vue.extend({
      name: 'connection_docs_suggest',
      components: {},
      props: {
        // Optional, for existing
        'integration_name': {
          default: null
        },
        'error': {
          default: null
        },
      },
      data() {
        return {}
      },

      computed: {},
      mounted() {
      },

      created() {
      },
      methods: {},
      watch: {}
    }
  ) </script>
