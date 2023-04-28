<template>
  <v-menu  persistent
           :close-on-click="false"
           :close-on-content-click="false"
           :offset-overflow="true"
           :position-x="150"
           :position-y="50"
           :min-width="400"

           :right="true"
           offset-y
           v-if="button"
           v-model="open">
      <v-card class="pa-4">
        <v-card-text>
          <v-tabs
            v-model="tab"
            @change="on_change_tab"
            background-color="#f0f0f0"
          >
            <v-tabs-slider color="secondary"></v-tabs-slider>

            <v-tab
              style="border-bottom: 1px solid #e0e0e0"
              v-for="item in ['Style', 'Actions']"
              :key="item"
            >
              {{ item }}
            </v-tab>
            <v-tabs-items v-model="tab">
              <v-tab-item :key="1">
                <div class="d-flex flex-column">
                  <v-text-field class="custom-text-field" label="Button Title" v-model="button.display_name"></v-text-field>
                  <slider-picker class="mb-4" v-model="button_color" @change="change_color"/>
                </div>
              </v-tab-item>
              <v-tab-item :key="2" class="pl-4 pr-4">
                <button_edit_workflow_creator
                  :button="button"
                  :project_string_id="project_string_id"

                ></button_edit_workflow_creator>
              </v-tab-item>
            </v-tabs-items>
          </v-tabs>
        </v-card-text>


        <v-card-actions class="d-flex justify-end">
          <v-btn color="primary" @click="close_menu">
            Close
          </v-btn>
          <v-btn color="success" @click="save">
            Save
          </v-btn>
        </v-card-actions>
      </v-card>
  </v-menu>

</template>

<script lang="ts">

import Vue from 'vue';
import label_schema_selector from '../label/label_schema_selector.vue'
import attribute_select from '../attribute/attribute_select.vue'
import button_edit_workflow_creator from './button_workflow_editor.vue'
import axios from '../../services/customInstance';
import {ActionCustomButton} from '../../types/ui_schema/Buttons'
import {CustomButtonWorkflow} from '../../types/ui_schema/CustomButtonWorkflow'
import {types} from "sass";
import String = types.String;
import {attribute_group_list} from "../../services/attributesService";
export default Vue.extend({
  name: 'ButtonEditContextMenu',
  components: {
    label_schema_selector,
    button_edit_workflow_creator,
    attribute_select
  },
  props: {
    'project_string_id': {type: String, required: true},
    'button': {
      required: true,

    }

  },
  mounted: async function(){
    if(this.button && this.button.action){
      await this.initialize_button_action_config()
    }
  },
  data() {
    // move context menu off the page out of view when hidden
    return {
      button_color: {},
      tab: 0,


      open: false,
      action: null,

    }
  },
  watch:{
    button: {
      handler: function (val){
        this.tab = 0
        this.initialize_button_action_config()
      },
    },
    button_color: {
      deep: true,
      handler: function(val){
        this.button.color = val.hex
      }
    },

  },
  computed: {
  },
  methods: {
    initialize_button_action_config: async function(){
      if(this.button.workflow){
        this.set_workflow(this.button.workflow)
      }
    },
    set_workflow: function(wf){
      this.button.workflow = new CustomButtonWorkflow(wf.actions)
    },
    open_menu: function(){
      this.open = true
    },
    close_menu: function(){
      this.open = false;
    },
    change_color: function(val){
      this.button.color = val
    },
    on_change_tab: async function(tab){
      if(tab === 1){
        await this.initialize_button_action_config()
      }
    },
    save: async function(){
      await this.$store.commit('update_custom_button', this.button.name, this.button)
      await this.update_ui_schema_with_servercall()
      this.open = false

    },
    get_ui_schema: function () {
      if (this.$store.state.ui_schema.current == undefined) {
        throw new Error("this.$store.state.ui_schema.current is undefined")
      }
      return this.$store.state.ui_schema.current
    },


    update_ui_schema_with_servercall: async function(){
      if (!this.get_ui_schema() || !this.get_ui_schema().id) {
        return
      }

      this.loading = true;
      this.error = {}

      try{
        const response = await axios.post(
          `/api/v1/project/${this.project_string_id}/ui_schema/update`,
          this.get_ui_schema()
        )
      }
      catch (error) {
        this.error = this.$route_api_errors(error)
        console.error(error)

      }
      finally {
        this.loading = false;
      }

    },
  }
});
</script>

<style>
.custom-text-field {
  font-size: 16px;
}
</style>
