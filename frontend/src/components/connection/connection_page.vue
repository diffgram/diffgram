<template>
  <div>

    <main_menu v-if="may_edit"
               height="60">
    </main_menu>
    <v-card class="pa-8">
      <h1>Create a new connection:</h1>
      <connection_form
        form_height="100%"
        form_width="100%"
        :connection_id="connection_id"
        :may_edit="may_edit"
        :show_return_button="true"
      >
      </connection_form>
    </v-card>


  </div>
</template>

<script lang="ts">


  /*  Caution, re adding new select controls
   *    expects  @change="has_changes = true"  otherwise won't "save"
   *
   *
   */

  import axios from 'axios';
  import connection_form from './connection_form';

  import Vue from "vue";

  export default Vue.extend({
      name: 'connection_page',
      components: {
        connection_form
      },
      props: {
        // Optional, for existing
        'connection_id': {
          default: null
        },
        'may_edit': {
          default: true,
          type: Boolean
        }
      },
      data() {
        return {

          success_loading_existing: false,
          success_saved: false,
          success_run: false,

          name: null,

          request_time: null,

          /*
           *
           */
          connection: {
            'name': 'My Connection',
            'archived': false,
            'permission_scope': 'project',
            'id': null,
            'integration_name': null,

            'private_id': null,
            'private_secret': null,
            'exists_private_secret_hash': null,
            'account_email': null,
            'project_id_external': null

          },


          // WIP
          google_list: [
            {
              'display_name': 'Cloud storage',
              'name': 'instance',
              'icon': 'mdi-google',
              'color': 'green'
            },
            {
              'display_name': 'AutoML',
              'name': 'instance',
              'icon': 'mdi-google',
              'color': 'green'
            },
          ],
          // WIP

          loading: false,
          error: {},
          result: null,

          auth: {},
          show_auth: false,

          has_changes: false,

          permission_level_list: ['Editor', 'Viewer'],
          permission_level: 'Editor',

        }
      },

      computed: {},
      mounted() {


      },

      created() {
        // Defaults
        this.project_string_id = this.$store.state.project.current.project_string_id
        this.org_id = this.$store.state.org.current.id

      },
      methods: {

      }
    }
  ) </script>
