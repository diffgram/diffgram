<template>
  <v-card elevation="0" class="ma-4 pa-4">
    <v-card-title class="d-flex align-center">
      <h2 class="d-flex">
        <span class="secondary--text font-weight-light">Project/{{ project_string_id }}/Templates/</span>
        <span class="font-weight-medium d-flex align-center">
              <span v-if="!edit_name">{{ instance_template ? instance_template.name : instance_template_name }}</span>
              <standard_button
                v-if="edit_name == false"
                tooltip_message="Edit Name"
                tooltip_direction="bottom"
                @click="edit_name = true"
                icon="edit"
                :icon_style="true"
                color="primary"
              >
              </standard_button>
        </span>
        <v-text-field
          v-if="edit_name"
          v-model="instance_template_name"
          @change="update_name"
          @keyup.enter="edit_name = false; has_changes = true"
          solo
          flat
          style="font-size: 22pt; border: 1px solid grey; height: 55px; margin-top: -10px"
          color="blue"
        >
        </v-text-field>

        <div>
          <standard_button
            v-if="edit_name"
            color="primary"
            icon="save"
            :icon_style="true"
            tooltip_message="Save Name Updates"
            confirm_message="Confirm"
            :loading="loading"
            :disabled="loading"
            @click="edit_name = false; has_changes = true"
          >
          </standard_button>
        </div>
      </h2>

      <div class="ml-auto">
        <v-btn color="success"
               class="mr-4 ml-4"
               data-cy="save_instance_template_button"
               text
               outlined
               @click="save_instance_template"
               :disabled="loading || !has_changes">
          <v-icon>mdi-content-save</v-icon>
          Save Instance Template
        </v-btn>
        <v-btn color="error"
               text
               outlined
               @click="is_open = false"
               :disabled="loading"
        >
          <v-icon>mdi-close</v-icon>
          Discard Changes
        </v-btn>

      </div>
    </v-card-title>
    <v-card-text>
      <instance_template_creation
        ref="instance_template_creation_tool"
        :project_string_id="project_string_id"
        :name="instance_template_name"
        :instance_template="instance_template"
        :schema_id="parseInt(schema_id)"
        @instance_template_create_success="on_instance_template_created"
      ></instance_template_creation>
    </v-card-text>

    <v-card-actions class="flex justify-end pa-0">

    </v-card-actions>

  </v-card>

</template>

<script lang="ts">
import Vue from "vue";
import axios from '../../services/customInstance';
import instance_template_creation from './instance_template_creation.vue'

export default Vue.extend({
  name: "instance_template_creation_page",
  props: {
    project_string_id: undefined,
    instance_template_name: 'New Instance Template',
    instance_template: undefined,
    has_changes: false,
    schema_id: {
      required: true
    },
  },
  components: {
    instance_template_creation: instance_template_creation,
  },
  data: function () {
    return {
      loading: false,
      edit_name: false,
    }
  },
  mounted() {

  },

  methods: {
    update_name: function(name){
      if(this.instance_template){
        this.instance_template.name = name
      }
    },
    save_instance_template: function () {
     if(this.$refs.instance_template_creation_tool){
       this.$refs.instance_template_creation_tool.save_instance_template()
     }
    },
    on_instance_template_created: function(){
      this.$router.push(`/project/${this.project_string_id}/labels?tab=templates`)
    },
  },

  computed: {
    instance_list() {
      if (this.instance) {
        return [this.instance]
      }
      return []
    }
  }

})
</script>

<style>
.dialog-instance-template {
  max-height: 100% !important;
  overflow: inherit !important;
}
</style>
