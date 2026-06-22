<template>
  <!-- Template section for the Project Migrator Configuration Step component -->
  <v-container fluid class="d-flex flex-column">
    <h1 class="font-weight-light">Configure</h1>

    <!-- Migration config Labelbox component, emits project_selected event -->
    <migration_config_labelbox
      ref="labelbox_config"
      @project_selected="on_project_selected"
      :project_string_id="project_string_id"
      :project_migration_data="project_migration_data"
      v-if="project_migration_data.connection && project_migration_data.connection.integration_name === 'labelbox'"
    ></migration_config_labelbox>

    <!-- Label schema selector component, emits change event -->
    <label_schema_selector
      :project_string_id="project_string_id"
      label="Select Diffgram Label Schema"
      @change="change_label_schema($event)"
    ></label_schema_selector>

    <!-- Wizard navigation component, emits next, back, and loading_next events -->
    <wizard_navigation
      @next="on_next_button_click"
      :loading_next="loading_steps"
      :disabled_next="loading_steps || !project_migration_data.labelbox_project_id"
      @back="$emit('previous_step')"
      :skip_visible="false"
    ></wizard_navigation>
  </v-container>
</template>

<script lang="ts">
// Import necessary components and services
import migration_config_labelbox from "./migration_config_labelbox";
import label_schema_selector from "../label/label_schema_selector.vue";
import { get_schemas } from "../../services/labelServices";
import Vue from "vue";

export default Vue.extend({
  // Component properties
  name: "project_migrator_config_step",
  components: {
    migration_config_labelbox,
    label_schema_selector,
  },
  props: {
    project_string_id: {
      default: null,
    },
    project_migration_data: {
      default: null,
    },
  },
  // Component data
  data() {
    return {
      step: 2,
      loading_steps: false,
      current_label_schema: null,
    };
  },
  computed: {},
  // Component methods
  async mounted() {
    await this.fetch_schemas();
  },
  methods: {
    on_project_selected: function () {
      // Handler for project_selected event from migration_config_labelbox
    },

    fetch_schemas: async function () {
      // Fetches label schemas for the given project_string_id
      const [result, error] = await get_schemas(this.project_string_id);
      if (error) {
        this.error = this.$route_api_errors(error);
      }
      if (result) {
        this.label_schema_list = result;
      }
    },

    change_label_schema: function (schema) {
      // Handler for change event from label_schema_selector
      this.project_migration_data.label_schema_id = schema.id;
      this.current_label_schema = schema;
    },

    on_next_button_click: function () {
      // Handler for next button click event
      this.$emit("next_step");
    },
  },
});
</script>
