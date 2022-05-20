<template>
  <div class="d-flex flex-column">

    <div  v-if="workflow.actions_list.length > 0">
      <div

        v-for="(action, index) in workflow.actions_list"
        :key="index"
        class="d-flex flex-column align-center justify-center"
      >
        <v-icon  size="48" v-if="index > 0">mdi-arrow-down</v-icon>
        <action_node_box
          @remove="on_remove_action"
          @open_action_selector="on_open_action_selector"
          @add_action_to_workflow="on_add_action_to_workflow"
          @select_action="on_select_action($event)"
          :action="action"
          :actions_list="workflow.actions_list"
          :project_string_id="project_string_id"
        />

      </div>
    </div>
    <div v-else class="d-flex flex-column align-center justify-center">
      <h1 class="font-weight-light mb-4">No steps yet.</h1>
      <h3 class="font-weight-light text-center">Add A Step to Your Workflow by clicking a step on the right</h3>
      <v-icon size="96">mdi-sitemap-outline</v-icon>
    </div>
  </div>
</template>

<script lang="ts">

  import axios from '../../services/customInstance';
  import action_step_box from './action_step_box'
  import action_node_box from './action_node_box'

  import Vue from "vue";

  export default Vue.extend({

      name: 'workflow_steps_visualizer',

      components: {
        action_step_box: action_step_box,
        action_node_box: action_node_box
      },
      props: {
        'project_string_id': {
          default: null
        },
        'workflow': {
          type: Object,
          default: null
        },
        'selected_action': {
          type: Object,
          default: null
        }
      },

      data() {
        return {
          loading: false,
          error: {},
          holder: [],
          dragging: false,



        }
      },
      computed: {},
      methods: {
        on_open_action_selector: function(){
          this.$emit('open_action_selector')
        },
        on_select_action: function(act){
          this.$emit('select_action', act)
        },
        on_add_action_to_workflow: function(act){
          this.$emit('add_action_to_workflow', act)
        },
        onDragStartNewBlock (event) {
          console.log('onDragStartNewBlock', event);
          // contains all the props and attributes passed to demo-node
          const { props } = event
          this.newDraggingBlock = props;
          this.$emit('newDraggingBlock', props)
        },
        onDragStopNewBlock (event) {
          console.log('onDragStopNewBlock', event);
          this.newDraggingBlock = null;
          this.$emit('newDraggingBlock', null)
        },
        on_remove_action: function(act){
          console.log('on_remove_node', act)
          this.$emit('remove_selection')
        }

      }
    }
  ) </script>
