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
