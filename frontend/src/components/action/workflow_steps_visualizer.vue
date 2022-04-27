<template>
  <div class="d-flex flex-column">

    <div>
      <div
        v-for="(action, index) in workflow.actions_list"
        :key="index"
        class="d-flex flex-column align-center justify-center"
      >
        <v-icon  size="48" v-if="index > 0">mdi-arrow-down</v-icon>
        <action_node_box
          style="min-width: 300px;"
          @remove="on_remove_action"
          @add_action_to_workflow="on_add_action_to_workflow"
          @select_action="on_select_action"
          :action="action"
          :actions_list="workflow.actions_list"
        />

      </div>
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
        on_select_action: function(act){
          this.$emit('select_action', act)
        },
        on_add_action_to_workflow: function(act){
          this.workflow.actions_list.push(act)
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
        }

      }
    }
  ) </script>
