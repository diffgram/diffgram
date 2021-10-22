<template>
  <div
    class="context-menu"
    :class="{visible: show_context_menu}"
    :style="{top: top, left: left}"
  >
    <!-- Instance context -->
    <v-card

      class="mx-auto"
      max-width="300"
      tile
    >

      <v-list-item
        link
        dense
        data-cy="set_node_name_dialog_button"
        v-if="node_hover_index_locked != undefined"
        @click="on_click_set_node_name()"
      >

        <v-list-item-icon>
          <tooltip_icon
            tooltip_message="Set Node Name"
            icon="mdi-rename-box"
            color="primary"
          ></tooltip_icon>
        </v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title class="pr-4">
            Set Node Name
          </v-list-item-title>
        </v-list-item-content>

      </v-list-item>

      <v-menu
        v-if="show_set_node_name_menu"
        v-model="show_set_node_name_menu"
        :allow-overflow="true"
        :offset-overflow="true"
        :close-on-click="false"
        :close-on-content-click="false"
        :attach="true"
        :z-index="99999999"
      >
        <node_name_editor_keypoint_instance
          :node_index="node_hover_index_locked"
          :instance="instance"
          :instance_list="instance_list"
          :instance_index="instance_hover_index_locked"
          @close="on_close_node_name_menu"
          @node_updated="on_node_updated"
        ></node_name_editor_keypoint_instance>
      </v-menu>

      <v-list-item
        link
        dense
        data-cy="mark_occluded_button"
        v-if="node_hover_index_locked != undefined"
        @click="on_click_occluded()"
      >

        <v-list-item-icon>
          <tooltip_icon
            tooltip_message="Mark Occluded"
            icon="mdi-vector-polyline-minus"
            color="primary"
          ></tooltip_icon>
        </v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title class="pr-4">
            Mark Occluded
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>

    </v-card>

  </div>

</template>

<script lang="ts">
  import Vue from 'vue';

  /**
   * @vue-prop {object} mouse_position - Current position of mouse
   * @vue-prop {boolean} show_context_menu - Flag for context_menu visibility
   * @vue-prop {number} instance_hover_index - instance object index number
   * @vue-data {string} top - Position of context menu from top of page
   * @vue-data {string} left - Position of context menu from left of page
   * @vue-event {string} get_mouse_position - Updates this.top and this.left from mouse position
   * @vue-event {object} on_click_delete_instance Delete click handler for context menu item "Delete"
   */

  import user_icon from '../user/user_icon.vue';
  import share_instance_dialog from '../share/share_instance_dialog.vue';
  import node_name_editor_keypoint_instance from '../annotation/node_name_editor_keypoint_instance';
  import sequence_select from '../video/sequence_select.vue'
  import {KeypointInstance} from "../vue_canvas/instances/KeypointInstance";

  export default Vue.extend({
    name: 'context_menu_instance_template',
    components: {
      user_icon,
      share_instance_dialog,
      node_name_editor_keypoint_instance,
      sequence_select
    },
    props: {
      'mouse_position': {
        type: Object,
        default: null,
      },
      'selected_instance_index': {
        type: Number,
        default: null,

      },
      'instance_clipboard': {
        type: Object,
        default: null,

      },
      'project_string_id': {
        type: String,
        default: null
      },
      'show_context_menu': {
        type: Boolean,
      },
      'instance_hover_index': {
        type: Number,
        default: null,
      },
      'instance_list': {
        type: Array,
        default: null,
      },
      'instance':{
        type: KeypointInstance,
        default: null
      }

    },
    data() {
      // move context menu off the page out of view when hidden
      return {
        top: '-1000px',
        left: '-1000px',
        instance_hover_index_locked: null,
        hovered_figure_id_locked: null,
        polygon_point_hover_locked: null,
        instance_template_name: null,
        instance_index_to_paste: null,
        instance_index_to_create_instance_template: null,
        show_share_instance_menu: false,
        show_merge_polygon_menu: false,
        show_instance_template_menu: false,
        show_set_node_name_menu: false,
        show_paste_menu: false,
        x: 0,
        y: 0,
        num_frames: 1,
        locked_mouse_position: undefined,
        show_issue_panel: false,
        node_hover_index_locked: undefined

      }
    },

    computed: {

    },

    watch: {
      show_context_menu(isVisible) {


        if (isVisible == true) {
          // lock mouse position on click only
          this.get_mouse_position();
          this.instance_hover_index_locked = this.instance_hover_index
          this.node_hover_index_locked = this.instance.node_hover_index

          // We want to free condition on null in template so "normalize" it here.
          if (isNaN(this.instance_hover_index_locked)) {
            this.instance_hover_index_locked = null
          }

        } else {

          this.top = '-1000px';
          this.left = '-1000px';
          this.instance_hover_index_locked = null
          this.node_hover_index_locked = undefined
          this.show_set_node_name_menu = false;
        }
      },

    },
    methods: {
      emit_update_and_hide_menu: function(instance_update: Object) {

        this.$emit('instance_update', instance_update);
        this.$emit('hide_context_menu');
      },
      on_click_occluded: function(){
        if(!this.$props.instance){
          return
        }
        this.$props.instance.toggle_occluded();
      },
      on_node_updated: function(){
        let instance_update = {
          index: this.instance_hover_index_locked,
          node_hover_index: this.node_hover_index_locked,
          mode: "node_name_changed"
        }
        console.log('udpateddd')
        this.emit_update_and_hide_menu(instance_update)
      },


      on_close_node_name_menu: function(){
        this.$store.commit('set_user_is_typing_or_menu_open', false);
        this.show_set_node_name_menu = false;
      },
      on_click_set_node_name: function(){
        this.$store.commit('set_user_is_typing_or_menu_open', true);
        this.show_set_node_name_menu = true;
      },

      close() {
        this.$emit('close_context_menu');
        this.$store.commit('set_user_is_typing_or_menu_open', false)
        this.show_set_node_name_menu = false;
      },

      get_mouse_position: function () {
        if(!this.mouse_position){
          return
        }
        this.top = this.mouse_position.raw.y + 'px';
        this.left = this.mouse_position.raw.x + 'px';
        this.locked_mouse_position = {...this.mouse_position};
      },
    }
  });
</script>

<style>
  .context-menu {
    position: absolute;
    margin: 0;
    box-sizing: border-box;
    display: none;
    z-index: 100;
  }

  .context-menu.visible {
    display: block;
  }
</style>
