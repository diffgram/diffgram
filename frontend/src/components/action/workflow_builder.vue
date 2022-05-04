<template>
  <v-container fluid id="" style="height: 100%;">

    <v-card style=" min-height: 800px">
      <div class="d-flex" style="height: 100%">

        <v-card class="ml-2 mr-2 steps-container d-flex flex-column" width="20%" elevation="0" style="height: 100%">
          <v-card-title>Workflow:</v-card-title>
          <v-card-text class="align-stretch" style="height: 100%;">
            <workflow_steps_visualizer
              @add_action_to_workflow="on_add_action_to_workflow"
              @open_action_selector="show_add_action_panel"
              @remove_selection="on_remove_selection"
              @select_action="on_select_action"
              :workflow="workflow"
              @newDraggingBlock="on_new_dragging_block"
              :project_string_id="project_string_id">

            </workflow_steps_visualizer>
          </v-card-text>

        </v-card>

        <v-card v-if="selected_action && !show_add_action" class="ml-2 pa-4 steps-container" width="80%" elevation="0">
          <v-card-title v-if="selected_action.kind !== 'action_start'">
            <h3 class="font-weight-light">
              <v-icon size="32" color="primary">mdi-pencil</v-icon>
              Configure: {{ selected_action.name }}
            </h3>
          </v-card-title>
          <action_config_factory :actions_list="workflow.actions_list"
                                 :project_string_id="project_string_id"
                                 :action="selected_action">
          </action_config_factory>
        </v-card>
        <v-card v-if="show_add_action" class="ml-2 pa-4 steps-container" width="80%" elevation="0">
          <v-card-title>
            <h1 class="font-weight-light">
              <v-icon size="48" color="primary">mdi-plus</v-icon>
              Add New Step
            </h1>
          </v-card-title>
          <action_selector
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
import upload from '../upload_large.vue';
import workflow_run_list from './workflow_run_list.vue';
import {v4 as uuidv4} from 'uuid'

import Vue from "vue";
import Workflow_steps_visualizer from "./workflow_steps_visualizer.vue";

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
        loading: false,
        show_add_action: false,
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

      // for "updates in place" to page.
      // this is really stupid but vue js / router doesn't seem
      // to have better way to do this
      // have to do this on all components ...
      // and can't call this.created() for some reason

      flow_id() {
        this.api_get_flow()
      }


    },

    created() {
      if (this.$route.params.flow_id) {
        this.flow_id = this.$route.params.flow_id
        this.api_get_flow()
      }
    },
    mounted() {
      if (this.workflow.actions_list.length === 0) {
        this.show_add_action_panel();
      }
    },
    computed: {},
    methods: {
      on_add_action_to_workflow: function (act) {
        this.hide_add_action_panel()
        this.workflow.actions_list.push(act)
        this.on_select_action(act)
      },
      on_remove_selection: function () {
        this.selected_action = null
      },
      on_select_action: function (action) {
        this.selected_action = action;
        this.hide_add_action_panel();
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
      api_flow_new: function () {

        this.loading = true
        this.error = {}
        this.success = false

        axios.post(
          '/api/v1/project/' + this.project_string_id +
          '/actions/workflow/new',
          {
            name: this.flow.name,
            trigger_type: this.flow.trigger_type,
            time_window: this.flow.time_window

          }).then(response => {

          this.flow = response.data.flow;
          this.flow_id = this.flow.id;
          this.success = true
          this.loading = false

        }).catch(error => {

          if (error.response.status == 400) {
            this.error = error.response.data.log.error
          }
          this.loading = false
          console.log(error)
        });

      },
      change_trigger_type: function () {

      },
      api_get_flow: function () {

        if (!this.flow_id) {
          return
        }

        this.loading = true
        this.error = {}
        this.success = false

        axios.post(
          '/api/v1/project/' + this.project_string_id +
          '/flow/single',
          {
            flow_id: Number(this.flow_id),
            time_window: this.flow.time_window,
            name: this.flow.name,
            trigger_type: this.flow.trigger_type

          }).then(response => {

          this.flow = response.data.flow
          this.loading = false

        }).catch(error => {

          if (error.response.status == 400) {
            this.error = error.response.data.log.error
          }
          this.loading = false
          console.log(error)
        });

      },
      generateId(nodes) {
        let id = uuidv4()
        // _.find is a lodash function
        while (_.find(nodes, {id}) !== undefined) {
          id = uuidv4()
        }
        return id;
      },
      remove(event) {
        console.log('remove', event)

        // node we're dragging to
        const {node} = event

        // we use lodash in this demo to remove node from the array
        const nodeIndex = _.findIndex(this.nodes, {id: node.id});
        this.nodes.splice(nodeIndex, 1);
      },
      move(event) {
        console.log('move', event);

        // node we're dragging to and node we've just dragged
        const {dragged, to} = event;

        // change panentId to id of node we're dragging to
        dragged.parentId = to.id;
      },
      add(event) {
        // every node needs an ID
        const id = this.generateId();

        // add to array of nodes
        this.nodes.push({
          id,
          ...event.node,
        });
      },
      hide_add_action_panel: function () {
        this.show_add_action = false
      },
      show_add_action_panel: function () {
        this.show_add_action = true
      },
      api_flow_update: function (mode) {

        this.loading = true
        this.error = {}
        this.success = false

        axios.post(
          '/api/v1/project/' + this.project_string_id +
          '/actions/workflow/update',
          {
            flow_id: this.flow_id ? Number(this.flow_id) : undefined,
            name: this.flow.name,
            trigger_type: this.flow.trigger_type,
            time_window: this.flow.time_window,
            active: this.flow.active,
            mode: mode

          }).then(response => {

          this.flow = response.data.flow

          this.success = true
          this.loading = false


          // careful mode is local, not this.mode
          if (mode == 'ARCHIVE') {

            let url = '/project/' + this.project_string_id +
              '/flow/list'

            this.$router.push(url)

          }

        }).catch(error => {

          if (error.response.status == 400) {
            this.error = error.response.data.log.error
          }
          this.loading = false
          console.log(error)
        });

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
</style>
