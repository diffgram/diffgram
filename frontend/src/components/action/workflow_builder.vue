<template>
  <v-container fluid id="" style="height: 100%;">

    <v-card style=" min-height: 800px">
      <v_error_multiple :error="error"></v_error_multiple>
      <v-card-title>
        <div class="d-flex align-center justify-start " style="width: 100%">
          <h4 class="">
                <span>
                  Workflow:
                </span>
            <span class="secondary--text font-weight-light" v-if="workflow && !edit_name">
                  {{workflow.name }}
                </span>
          </h4>
          <standard_button
            v-if="!edit_name"
            tooltip_message="Change Name"
            @click="edit_name = true"
            icon="mdi-pencil"
            :icon_style="true"
            small
            color="primary"
            datacy="edit_schema_name_button"
          >
          </standard_button>

          <v-text-field
            class="edit-workflow-name"
            data-cy="schema_name_text_field"
            v-if="!loading && workflow && edit_name"
            v-model="workflow.name"
            @input="has_changes = true"
            @keyup.enter="update_workflow_name"
            solo
            flat
            height="35px"
            style="font-size: 18px; border: 1px solid grey; height: 35px; max-width: 450px;"
            color="blue"
          >
          </v-text-field>

          <div>
            <standard_button
              v-if="edit_name == true"
              @click="update_workflow_name"
              color="primary"
              icon="save"
              :icon_style="true"
              datacy="save_name_button"
              tooltip_message="Save Name Updates"
              confirm_message="Confirm"
              :loading="loading"
              :disabled="loading || !has_changes"
            >
            </standard_button>
          </div>

          <standard_button
            v-if="edit_name == true"
            tooltip_message="Cancel Name Edit"
            datacy="cancel_edit_name"
            @click="edit_name = false"
            icon="mdi-cancel"
            :icon_style="true"
            color="primary"
            class="flex-grow-1"
            :disabled="loading"
          >
          </standard_button>
          <div class="d-flex align-center justify-start ml-auto">
            <v-tooltip top primary class="">
              <template v-slot:activator="{ on, attrs }">
                <div v-on="on" v-bind="attrs">
                  <v-switch
                    @change="on_change_workflow_active"
                    color="success"
                    v-model="workflow.active"

                  >
                  </v-switch>
                </div>
              </template>
              <span>Active: </span>
            </v-tooltip>
            <button_with_confirm
              tooltip_message="Archive Workflow"
              button_message="Archive Workflow"
              @confirm_click="archive_workflow"
              icon="mdi-delete"
              :disabled="loading && !workflow"
              button_color="error"
              :icon_style="true"
              datacy_confirm="archive_schema_button_confirm"
              datacy="archive_schema_button"
            >
            </button_with_confirm>
          </div>
        </div>

      </v-card-title>
      <div class="d-flex" style="height: 100%">

        <v-card class="ml-2 mr-2 steps-container d-flex flex-column" width="20%" elevation="0" style="height: 100%">

          <v-card-text class="align-stretch" style="height: 100%;">
            <workflow_steps_visualizer
              @add_action_to_workflow="on_add_action_to_workflow"
              @open_action_selector="show_add_action_panel"
              @remove_selection="on_remove_selection"
              @remove_action="remove_action"
              @select_action="on_select_action($event, 'wizard')"
              :workflow="workflow"
              @newDraggingBlock="on_new_dragging_block"
              :project_string_id="project_string_id">

            </workflow_steps_visualizer>
          </v-card-text>

        </v-card>

        <v-card v-if="selected_action && !show_add_action" class="ml-2 pa-4 steps-container" width="80%" elevation="0">
          <v-progress-linear
            v-if="add_action_loading"
            height="50"
            class="ma-auto mr-4 ml-4"
            striped
            indeterminate>

          </v-progress-linear>

          <action_config_factory 
            v-if="!add_action_loading"
            :actions_list="workflow.actions_list"
            :project_string_id="project_string_id"
            :action="selected_action"
            :display_mode="display_mode"
            :workflow="workflow"
            @action_updated="on_action_updated"
            @open_action_selector="show_add_action_panel"
          />
        </v-card>
        <v-card v-if="show_add_action" class="ml-2 pa-4 steps-container" width="80%" elevation="0">
          <v-card-title>
            <h1 class="font-weight-light">
              <v-icon size="48" color="primary">mdi-plus</v-icon>
              Add New Step
            </h1>
          </v-card-title>
          <action_selector
            :project_string_id="project_string_id"
            @add_action_to_workflow="on_add_action_to_workflow"
          ></action_selector>
        </v-card>

      </div>

    </v-card>

  </v-container>
</template>

<script lang="ts">
import axios from '../../services/customInstance';
import action_existing_list from './action_existing_list.vue';
import action_selector from './action_selector.vue';
import action_node_box from './action_node_box.vue';
import action_config_factory from './action_config_factory.vue';
import {workflow_update, get_workflow, new_workflow, new_action, action_update} from './../../services/workflowServices';
import upload from '../upload_large.vue';
import workflow_run_list from './workflow_run_list.vue';
import {v4 as uuidv4} from 'uuid'

import Vue from "vue";
import Workflow_steps_visualizer from "./workflow_steps_visualizer.vue";
import sillyname from 'sillyname';
import {Action, initialize_action_list} from "./Action";
export default Vue.extend({

    name: 'workflow_builder',

    components: {
      action_config_factory,
      Workflow_steps_visualizer,
      action_node_box: action_node_box,
      action_existing_list: action_existing_list,
      upload: upload,
      workflow_run_list: workflow_run_list,
      action_selector: action_selector
    },
    props: {
      'project_string_id': {
        default: null
      },
      'workflow_id': {
        default: null
      }
    },

    data() {
      return {
        selected_action: null,
        trigger_types: [
          {name: 'Task is completed.', value: 'task_completed'},
          {name: 'Task is created.', value: 'task_created'},
          {name: 'Task Template is completed.', value: 'task_template_completed'},
          {name: 'Files are uploaded.', value: 'input_file_uploaded'},
          // {name: 'Instances are uploaded.', value: 'input_instance_uploaded'},
        ],
        time_windows: [
          {name: 'No Aggregation time.', value: '1_minute'},
          {name: '5 Minutes.', value: '5_minutes'},
          {name: '10 Minutes.', value: '10_minutes'},
          {name: '30 Minutes.', value: '30_minutes'},
          {name: '1 hour.', value: '1_hours'},
          {name: '4 hours.', value: '4_hours'},
          {name: '12 hours.', value: '12_hours'},
          {name: '1 Day', value: '1_days'},
        ],
        nodes: [
          {
            id: '1',
            parentId: -1,
            nodeComponent: 'action_node_box',
            data: {
              icon: 'mdi-clock-start',
              text: 'Workflow Trigger',
              title: 'Action Start',
              kind: 'action_start',
              description: 'Drop a trigger below to get started: ',
            },
          }
        ],
        add_action_loading: false,
        loading: false,
        has_changes: false,
        show_add_action: false,
        edit_name: false,
        over_drag_area: false,
        error: {},
        success: false,
        newDraggingBlock: null,
        workflow: {
          name: null,
          active: null,
          is_new: null,
          time_window: undefined,
          kind: null,
          actions_list: [],
        }
      }
    },

    watch: {
      workflow_id() {
        this.api_get_workflow()
      },
      selected_action: {
        deep: true,
        handler: function(new_val, old_val) {
          this.on_action_updated(new_val)
        }
      }


    },

    created() {

    },
    async mounted() {
      if(!this.$props.workflow_id){
        if (this.workflow.actions_list.length === 0) {
          this.show_add_action_panel();
        }
        this.workflow.name = sillyname()
      }
      else{
        await this.api_get_workflow()
        if (this.workflow.actions_list.length === 0) {
          this.show_add_action_panel();
        }
      }

    },
    computed: {
      display_mode: function(){
        if(this.workflow.active){
          return "ongoing_usage"
        }
        else{
          return "wizard"
        }
      }
    },
    methods: {
      remove_action: async function(action){
        action.archived = true
        await this.api_action_update(action)
        this.workflow.actions_list = this.workflow.actions_list.filter(act => action.id != act.id).sort((a, b) => {
          return a.position- b.position;
        })
        this.workflow.actions_list = this.workflow.actions_list.map((elm, index) => {
          return {
            ...elm,
            ordinal: index
          }
        })

      },
      on_change_workflow_active: function(value){
        this.workflow.active = value
        this.api_workflow_update()
      },
      update_workflow_name: function(){
        this.edit_name = false
        this.api_workflow_update()
      },
      on_add_action_to_workflow: async function (action_template) {
        this.add_action_loading = true
        this.hide_add_action_panel()
        if(!this.workflow.id){
          await this.api_workflow_new()
        }
        let action = {
          ...action_template,
          template_id: action_template.id,
          id: undefined,
          ordinal: this.workflow.actions_list.length
        }
        let new_action  = await this.api_action_new(action)
        if (!new_action){
          return
        }

        this.workflow.actions_list.push(new_action)

        Vue.set(this.workflow.actions_list, this.workflow.actions_list.length - 1, new_action)
        this.workflow = {
          ...this.workflow
        }
        this.on_select_action(new_action)
      },
      on_remove_selection: function () {
        this.selected_action = null
      },
      on_select_action: function (action) {
        this.selected_action = action;
        this.hide_add_action_panel();
        this.add_action_loading = false
      },
      on_new_dragging_block: function (block) {
        this.newDraggingBlock = block;
      },
      update_or_new: function () {
        if (this.flow_id) {
          this.api_flow_update("UPDATE");
        } else {
          this.api_flow_new();
        }
      },
      api_action_new: async function (action) {

        this.loading = true
        this.error = {}
        this.success = false
        let [result, err] = await new_action(this.project_string_id, this.workflow.id, action)
        if(err){

          this.error = this.$route_api_errors(err)
          this.loading = false
          console.error(err)
          return false
        }
        if(result){
          this.success = true
          this.loading = false
          let action = new Action(
            result.action.public_name,
            result.action.icon,
            result.action.kind,
            result.action.trigger_data,
            result.action.precondition,
            result.action.description,
            result.action.completion_condition_data
          )
          action.setFromObject(result.action)
          return action
        }

      },
      api_workflow_new: async function () {

        this.loading = true
        this.error = {}
        this.success = false
        let [result, err] = await new_workflow(this.project_string_id, this.workflow)
        if(err){

          if (err.response.status == 400) {
            this.error = err.response.data.log.error
          }
          this.loading = false
          console.error(err)
        }
        if(result){
          this.workflow = result.workflow;
          this.workflow.actions_list = [];
          this.success = true
          this.loading = false
          this.$router.push(`/project/${this.project_string_id}/workflow/${this.workflow.id}`)
        }

      },
      change_trigger_type: function () {

      },
      initialize_actions: function(action_list){
        return initialize_action_list(action_list)
      },
      api_get_workflow: async function () {

        if (!this.workflow_id) {
          return
        }

        this.loading = true
        this.error = {}
        this.success = false
        let [result, err] = await get_workflow(this.project_string_id, this.workflow_id)
        if(err){
          if (err.response.status == 400) {
            this.error = err.response.data.log.error
          }
          this.loading = false
          console.error(err)
        }
        if(result){
          this.workflow = result.workflow
          this.workflow.actions_list = this.initialize_actions(this.workflow.actions_list)
          if(this.workflow.actions_list.length > 0){
            this.on_select_action(this.workflow.actions_list[0], 'wizard')
          }
          this.loading = false
        }
      },
      hide_add_action_panel: function () {
        this.show_add_action = false
      },
      show_add_action_panel: function () {
        this.show_add_action = true
      },
      archive_workflow: async function(){
        await this.api_workflow_archive()
      },
      on_action_updated: async function(act){
        await this.api_action_update(act)
      },
      api_action_update: async function(act){
        this.loading = true;
        this.error = {};
        this.success = false;
        let [result, err] = await action_update(this.project_string_id, this.workflow.id, act)
        if(err){
          if (err.response.status == 400) {
            this.error = err.response.data.log.error
          }
          this.loading = false
          console.error(err)
          return
        }
        if(result){
          this.success = true
          this.loading = false
        }
      },
      api_workflow_archive: async function(){
        // careful mode is local, not this.mode
        this.loading = true;
        this.error = {};
        this.success = false;
        let [result, err] = await workflow_update(this.project_string_id, this.workflow, "ARCHIVE")
        if(err){
          if (err.response.status == 400) {
            this.error = err.response.data.log.error
          }
          this.loading = false
          console.error(err)
          return
        }
        if(result){
          this.workflow = result.workflow

          this.success = true
          this.loading = false
          let url = `/project/${this.project_string_id}/workflow/list`
          this.$router.push(url)
        }

      },
      api_workflow_update: async function () {
        this.loading = true;
        this.error = {};
        this.success = false;

        let [result, err] = await workflow_update(this.project_string_id, this.workflow, "UPDATE")
        if(err){
          if (err.response.status == 400) {
            this.error = err.response.data.log.error
          }
          this.loading = false
          console.log(err)
          return
        }
        if(result){
          this.workflow = result.workflow

          this.success = true
          this.loading = false
        }
      }

    }
  }
) </script>
<style>
.steps-container {
  min-height: 700px !important;
  border: 1px solid #e0e0e0 !important;
}

.on-drag {
  background: #a1cdff;
  transition: 0.5s ease;
}
.edit-workflow-name .v-input__control{
  min-height: 5px !important;
  height: 40px !important;
}

</style>
