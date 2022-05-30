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
