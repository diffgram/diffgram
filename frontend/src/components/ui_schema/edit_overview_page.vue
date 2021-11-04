<template>
  <div v-cloak >
  <v-container fluid>

    <div class="d-flex mb-8 justify-space-between">

      <h1 class="font-weight-medium text--primary mr-4">

        White-label Customization (BETA)
      </h1>

      <tooltip_button
        tooltip_message="Launch UI Editor"
        @click="open_ui_schema_creation"
        button_color="primary"
        icon="mdi-puzzle-edit"
        :left="true"
        button_message="Launch UI Editor"
        color="white">
      </tooltip_button>

    </div>

    <p class="text--primary">
      UI Schemas are a way to Customize the Annotation UI. You can show/hide buttons and configure
      what you want the annotators to see beyond Label Schema.
    </p>

    <v-container fluid>

      <ui_schema_selector
        data-cy="ui-schema-selector"
        :project_string_id="$store.state.project.current.project_string_id"
        :show_default_option="true"
                          >
      </ui_schema_selector>

    </v-container>

  </v-container>

  </div>
</template>

<script lang="ts">

import Vue from "vue";
import ui_schema_selector from './ui_schema_selector'

export default Vue.extend({
    name: 'ui_schema_edit_overview_page',

    props: {
    },
    watch: {},

    components: {
        ui_schema_selector
    },

    mounted() {

     

    },
    data() {
      return {
      }
    },
    methods: {     
      open_ui_schema_creation: function () {
        let routeData = this.$router.resolve({
          path: `/task/-1`,
          query: {
            edit_schema: true,
            create_new_on_load: false,
            view_only: true
            }
        });
        window.open(routeData.href, '_blank');
      },
    }
  }
) </script>
<style scoped>

</style>
