<template>
  <div class="d-flex flex-column">
    <div>Drag blocks to the node tree below using the drag handle</div>
    <div>
      <flowy-new-block
        v-for="(block, index) in blocks"
        :key="index"
        class="q-mr-md"
        @drag-start="onDragStartNewBlock"
        @drag-stop="onDragStopNewBlock"
      >
        <template v-slot:preview="{}">
          <action_step_box
            :title="block.preview.title"
            :description="block.preview.description"
          />
        </template>
        <template v-slot:node="{}">
          <demo-node
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
  import "@hipsjs/flowy-vue/dist/lib/flowy-vue.css";
  import action_step_box from './action_step_box'

  import Vue from "vue";

  export default Vue.extend({

      name: 'workflow_steps_visualizer',

      components: {
        action_step_box: action_step_box
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
              preview: {
                title: 'New visitor',
              },
              node: {
                title: 'New visitor',
                description: '<span>When a <b>new visitor</b> goes to <b>Site 1</span></span>',
              },
            },
            {
              preview: {
                title: 'Update database',
                icon: 'error',
              },
              node: {
                title: 'Update database',
                description: '<span>Triggers when somebody performs a <b>specified action</b></span>',
              },
            },
            {
              preview: {
                title: 'Time has passed',
              },
              node: {
                title: 'Time has passed',
                description: 'Triggers after a specified <b>amount</b> of time',
              },
            },
            {
              preview: {
                title: 'Cannot be added',
              },
              node: {
                title: 'Time has passed',
                description: 'Triggers after a specified <b>amount</b> of time',
                canBeAdded: false,
              },
            },
          ],
          nodes: [
            {
              id: '1',
              parentId: -1,
              nodeComponent: 'demo-node',
              data: {
                text: 'Parent block',
                title: 'New Visitor',
                description: '<span>When a <b>new visitor</b> goes to <i>Site 1</i></span>',
              },
            },
            {
              id: '2',
              parentId: '1',
              nodeComponent: 'demo-node',
              data: {
                text: 'Parent block',
                title: 'New Visitor',
                description: '<span>When a <b>new visitor</b> goes to <i>Site 1</i></span>',
              },
            },
            {
              id: '3',
              parentId: '1',
              nodeComponent: 'demo-node',
              data: {
                text: 'Parent block',
                title: 'New Visitor',
                description: '<span>When a <b>new visitor</b> goes to <i>Site 1</i></span>',
              },
            },
          ]
        }
      },
      computed: {},
      methods: {
        onDragStartNewBlock (event) {
          console.log('onDragStartNewBlock', event);
          // contains all the props and attributes passed to demo-node
          const { props } = event
          this.newDraggingBlock = props;
        },
        onDragStopNewBlock (event) {
          console.log('onDragStopNewBlock', event);
          this.newDraggingBlock = null;
        },

      }
    }
  ) </script>
