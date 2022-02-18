<template>
  <div id="">

    <v-btn @click="api_flow_new"
           color="primary"
           text
           style="text-transform: none !important;"
           :loading="loading"
           :disabled="loading">
      <v-icon left>mdi-auto-fix</v-icon>
      New Email Alert or Webhook
    </v-btn>

    <v_error_multiple :error="error">
    </v_error_multiple>

  </div>
</template>

<script lang="ts">
  import Vue from "vue";

  export default Vue.extend({

      name: 'new_flow_button',

      components: {},
      props: {
        'project_string_id': {
          default: null
        }
      },
      data() {
        return {

          loading: false,
          error: {},
          success: false,

          flow: {}
        }
      },
      computed: {},
      methods: {

        api_flow_new: function () {
          let url = `/project/${this.project_string_id}/flow/`
          this.$router.push(url);
        }

      }
    }
  ) </script>
