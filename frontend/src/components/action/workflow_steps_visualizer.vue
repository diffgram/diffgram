<template>
  <div class="d-flex flex-column">

    <div>
      <flowy-new-block
        v-for="(block, index) in blocks"
        :key="index"
        @drag-start="onDragStartNewBlock"
        @drag-stop="onDragStopNewBlock"
      >
        <template v-slot:preview="{}">
          <action_step_box
            :is_trigger="block.is_trigger"
            :icon="block.icon"
            :kind="block.kind"
            :type="block.type"
            :title="block.preview.title"
            :description="block.preview.description"
          />
        </template>
        <template v-slot:node="{}">
          <action_node_box
            @remove="on_remove_node"
            :is_trigger="block.is_trigger"
            :icon="block.icon"
            :kind="block.kind"
            :type="block.type"
            :title="block.node.title"
            :description="block.node.description"
            :custom-attribute="block.node.canBeAdded"
          />
        </template>
      </flowy-new-block>
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
          default: null
        }
      },

      data() {
        return {
          loading: false,
          error: {},
          holder: [],
          dragging: false,
          blocks: [
            {
              is_trigger: true,
              icon: 'mdi-folder-arrow-up',
              kind: 'file_upload',
              preview: {
                title: 'Any New Data',
              },
              node: {
                title: 'On File Uploaded',
                description: 'When a file is uploaded',
              },
            },
            {
              is_trigger: true,
              icon: 'mdi-folder-arrow-up',
              kind: 'file_upload',
              preview: {
                title: 'Receive Data from Pre-Label',
              },
              node: {
                title: 'On File Uploaded',
                description: 'When a file is uploaded',
              },
            },
            {
              is_trigger: false,
              icon: 'mdi-folder-arrow-up',
              kind: 'file_upload',
              preview: {
                title: 'Generate Export',
              },
              node: {
                title: 'Generate Export',
                description: '...........',
              },
            },
            {
              is_trigger: false,
              icon: 'mdi-folder-arrow-up',
              kind: 'file_upload',
              preview: {
                title: 'Push Data to a Bucket',
              },
              node: {
                title: 'Push Data to a Bucket',
                description: '...........',
              },
            },
            {
              is_trigger: false,
              icon: 'mdi-folder-arrow-up',
              kind: 'file_upload',
              preview: {
                title: 'Run Custom Code',
              },
              node: {
                title: 'Run Custom Code',
                description: '...........',
              },
            },
            {
              is_trigger: true,
              icon: 'mdi-folder-arrow-up',
              kind: 'manual',
              preview: {
                title: 'Manual Trigger',
              },
              node: {
                title: 'On Manual Trigger',
                description: '...',
              },
            },
            {
              is_trigger: false,
              icon: 'mdi-checkbox-multiple-marked-outline',
              kind: 'create_tasks',
              preview: {
                title: 'Human Tasks',
              },
              node: {
                title: 'Human Tasks',
                description: 'Add tasks to a task template',
              },
            },
            {
              is_trigger: false,
              icon: 'mdi-brain',
              kind: 'run_inferences',
              preview: {
                title: 'Run Pre-Label',
              },
              node: {
                title: 'Run Pre-Label',
                description: 'Run model and add labels to the file',
              },
            },
            {
              is_trigger: false,
              kind: 'webhook',
              icon: 'mdi-code-braces-box',
              preview: {
                title: 'POST to Webhook',
              },
              node: {
                title: 'POST to Webhook',
                description: 'Send data to a given webhook.',
              },
            },
            {
              is_trigger: false,
              icon: 'mdi-filter',
              kind: 'filter',
              preview: {
                title: 'Filter Data',
              },
              node: {
                title: 'Filter Data',
                description: '...',
              },
            },
            {
              is_trigger: false,
              icon: 'mdi-filter',
              kind: 'filter',
              preview: {
                title: 'Start Training',
              },
              node: {
                title: 'Start Training',
                description: '...',
              },
            },
            {
              is_trigger: false,
              icon: 'mdi-filter',
              kind: 'filter',
              preview: {
                title: 'Alert / Email',
              },
              node: {
                title: 'Alert / Email',
                description: '...',
              },
            },
            {
              is_trigger: false,
              icon: 'mdi-filter',
              kind: 'filter',
              preview: {
                title: 'Task Milestone Reached',
              },
              node: {
                title: 'Task Milestone Reached',
                description: '...',
              },
            },
            {
              is_trigger: false,
              icon: 'mdi-filter',
              kind: 'filter',
              preview: {
                title: 'Loop Back to a Step',
              },
              node: {
                title: 'Loop Back to a Step',
                description: '...',
              },
            },
            {
              is_trigger: false,
              icon: 'mdi-filter',
              kind: 'filter',
              preview: {
                title: 'Loop Back to a Step',
              },
              node: {
                title: 'Loop Back to a Step',
                description: '...',
              },
            },
            {
              is_trigger: false,
              icon: 'mdi-filter',
              kind: 'filter',
              preview: {
                title: 'Human Supervision Control Point',
              },
              node: {
                title: 'Human Supervision Control Point',
                description: '...',
              },
            },

          ],

        }
      },
      computed: {},
      methods: {
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
        on_remove_node: function(node){
          console.log('on_remove_node', node)
        }

      }
    }
  ) </script>
