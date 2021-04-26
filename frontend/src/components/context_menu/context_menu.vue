<script lang="ts">
  import Vue from 'vue';
  import axios from 'axios';

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
  import sequence_select from '../video/sequence_select.vue'

  export default Vue.extend({
    name: 'ContextMenu',
    components: {
      user_icon,
      share_instance_dialog,
      sequence_select
    },
    props: {
      'mouse_position': {
        type: Object,
        default: null,
      },
      'task':{
        type: Object,
        default: null,

      },
      'draw_mode':{
        type: Boolean,
        default: null,
      },
      'selected_instance_index':{
        type: Number,
        default: null,

      },
      'instance_clipboard':{
        type: Object,
        default: null,

      },
      'project_string_id':{
        type: String,
        default: null
      },
      'polygon_point_hover_index':{
        type: Number,
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
      'video_mode': {
          type: Boolean,
          default: null,
       },
      'sequence_list': {
          type: Array,
          default: null,
       }

    },
    data() {
      // move context menu off the page out of view when hidden
      return {
        top: '-1000px',
        left: '-1000px',
        instance_hover_index_locked: null,
        polygon_point_hover_locked: null,
        instance_template_name: null,
        instance_index_to_paste: null,
        instance_index_to_create_instance_template: null,
        show_share_instance_menu: false,
        show_instance_template_menu: false,
        show_paste_menu: false,
        x: 0,
        y: 0,
        num_frames: 1,
        locked_mouse_position: undefined,
        show_issue_panel: false,

      }
    },

    computed: {
      selected_instance: function(){
        let selected = this.instance_list[this.instance_hover_index_locked]
        if (selected){
          return selected
        } else {
          return {}
        }
      },
      member: function () {
        return this.$store.state.project.current.member_list.find(x => {
          return x.member_id == this.instance_list[
            this.instance_hover_index_locked].member_created_id
        })
      },

    },

    watch: {
      show_context_menu(isVisible) {
        /* The big assumption here is that in annotation core
         * detect_clicks_outside_context_menu() watches
         *  if (e.target.matches('.context-menu, .context-menu *')){}
         *  and skips if it's a match.
         *
         *  CAUTION Some vuetify components break the css class,
         *  so we need to add :attach="true" to bring them back to this.
         *  (It's more fundamental then say just caching hover_index)
         *
         *  Tried to pass the class down however vuetify messes with it,
         *  in hard to predict ways, eg the 'block' style will be applied, but it will
         *  remove the part used for the above event tracking seeks.
         *  Where as if we use ` attach ` it appears to respect it.
         */

        if (isVisible == true) {
          // lock mouse position on click only
          this.get_mouse_position();
          this.instance_hover_index_locked = this.instance_hover_index
          this.polygon_point_hover_locked = this.$props.polygon_point_hover_index

          // We want to free condition on null in template so "normalize" it here.
          if (isNaN(this.instance_hover_index_locked)) {
            this.instance_hover_index_locked = null
          }

        } else {

          this.top = '-1000px';
          this.left = '-1000px';
          this.instance_hover_index_locked = null
          this.show_paste_menu = false;
          this.show_instance_template_menu = false;
        }
      },

      /*
       *
       * Future option, could watch index hover and hide show
       * based on this, but not there yet.
      instance_hover_index(index) {

        // we could also "close" the context menu
        // this.$emit('hide_context_menu');
      }
      */

    },
    methods: {
      show_instance_history_panel: function(){
        this.$emit('open_instance_history_panel',  this.instance_hover_index_locked);
      },
      close_instance_history_panel: function(){
        this.$emit('close_instance_history_panel',  this.instance_hover_index_locked);
      },
      display_paste_menu: function(e){
        this.show_paste_menu = false
        this.x = e.clientX
        this.y = e.clientY
        const hovered_instance_index = this.instance_hover_index_locked;
        this.instance_index_to_paste = hovered_instance_index;
        this.show_paste_menu = true
      },
      on_click_create_instance_template: function(e){
        this.show_instance_template_menu = false
        const hovered_instance_index = this.instance_hover_index_locked;
        this.instance_index_to_create_instance_template = hovered_instance_index;
        this.show_instance_template_menu = true
      },
      open_issue_panel(){
        this.$store.commit('set_user_is_typing_or_menu_open', true);
        this.$emit('open_issue_panel', this.locked_mouse_position);

      },
      close(){
        this.$emit('close_context_menu');
        this.$store.commit('set_user_is_typing_or_menu_open', false)
      },
      close_issue_dialog(){
        this.$store.commit('set_user_is_typing_or_menu_open', false);
        this.show_issue_dialog = false;
      },
      get_mouse_position: function () {
        this.top = this.mouse_position.raw.y + 'px';
        this.left = this.mouse_position.raw.x + 'px';
        this.locked_mouse_position = {...this.mouse_position};
      },

      change_sequence(event) {
        let instance_update = {
          index: this.instance_hover_index_locked,
          mode: "change_sequence",
          sequence: event
        }
        //console.log(instance_update)
        this.emit_update_and_hide_instance(instance_update)

      },

      on_click_delete_instance() {
        let instance_update = {
          index: this.instance_hover_index_locked,
          mode: "delete"
        }
        this.emit_update_and_hide_instance(instance_update)
      },
      show_share_context_menu() {
        this.show_share_instance_menu = true;
        this.$store.commit('set_user_is_typing_or_menu_open', true);
        this.$emit('share_dialog_open');

      },
      on_click_copy_instance(){
        this.$emit('copy_instance', this.instance_hover_index_locked);
        this.close();
      },
      emit_paste_to_next_frames(){
        this.$emit('paste_instance_on_next_frames', this.num_frames, this.instance_index_to_paste);
        this.close();
        this.show_paste_menu = false;
        this.num_frames = 1;
        this.instance_index_to_paste = undefined;
      },
      create_instance_template(){
        this.$emit('create_instance_template', this.instance_index_to_create_instance_template, this.instance_template_name);
        this.close();
        this.show_instance_template_menu = false;
        this.instance_index_to_paste = undefined;
      },
      on_click_paste_instance(){
        this.$emit('paste_instance');
        this.close();
      },
      close_share_dialog() {
        this.show_share_instance_menu = false;
        this.$store.commit('set_user_is_typing_or_menu_open', false);
        this.$emit('share_dialog_close')

      },
      on_click_delete_polygon_point(){
        this.$emit('delete_polygon_point', this.polygon_point_hover_locked);
      },
      emit_update_and_hide_instance(instance_update: Object) {

        if (this.instance_hover_index_locked == undefined) {
          return
        }

        this.$emit('instance_update', instance_update);
        this.$emit('hide_context_menu');
      }
    }
  });
</script>
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

      <!--  Change Sequence -->
      <!-- I like idea of hiding this behind a button but seems like
        it adds an extra step maybe-->
      <!--
      <v-list-item
        link
      >
        <v-list-item-icon>
          <tooltip_icon
            tooltip_message="Change Sequence"
            icon="mdi-delta"
            color="primary"
          />
        </v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title class="pr-4">
            Change Sequence
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
      -->

      <div v-if="video_mode == true">
        <sequence_select
          v-if="instance_hover_index_locked != undefined"
          class="pt-2 pl-4 pr-4"
          :sequence_list="sequence_list"
          :select_this_id="selected_instance.sequence_id"
          :attach="true"
          @change="change_sequence($event)">
          <!-- Important attach must be true otherwise it
            won't be part of the event detection for clicking,
            and the hover index will become None-->
        </sequence_select>
      </div>

      <v-list-item
        dense
        v-if="!draw_mode && video_mode && (instance_hover_index_locked != null || instance_clipboard)"
        @click="display_paste_menu"
      >

        <v-list-item-icon>
          <tooltip_icon
            tooltip_message="Paste Instance"
            icon="mdi-clipboard-multiple-outline"
            color="primary"
          />
        </v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title class="pr-4">
            Paste on Next Frames
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>


      <v-menu

        v-model="show_paste_menu"
        :allow-overflow="true"
        :offset-overflow="true"
        :close-on-click="false"
        :close-on-content-click="false"
        :attach="true"
        :z-index="999999"
      >
        <v-card>
          <v-card-title>Paste Instances: </v-card-title>
          <v-card-text>
            Paste instance to the next
            <v-text-field
                v-model="num_frames"
                @focus="$store.commit('set_user_is_typing_or_menu_open', true)"
                @blur="$store.commit('set_user_is_typing_or_menu_open', false)"
                          ></v-text-field>
            Frames ahead.

          </v-card-text>
          <v-card-actions>
            <v-btn @click="show_paste_menu = false,
                           $store.commit('set_user_is_typing_or_menu_open', false)">Close</v-btn>
            <v-btn @click="emit_paste_to_next_frames" color="success">Paste</v-btn>
          </v-card-actions>
        </v-card>
      </v-menu>

      <v-list-item
        link
        dense
        v-if="instance_clipboard && !draw_mode"
        data-cy="paste_instance"
        @click="on_click_paste_instance"
      >
        <v-list-item-icon>
          <tooltip_icon
            tooltip_message="Paste Instance"
            icon="mdi-content-paste"
            color="primary"
          />
        </v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title class="pr-4">
            Paste Instance
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>


      <v-list-item
        link
        dense
        data-cy="copy_instance"
        v-if="instance_hover_index_locked != null && !draw_mode"
        @click="on_click_copy_instance"
      >
        <v-list-item-icon>
          <tooltip_icon
            tooltip_message="Copy"
            icon="mdi-content-copy"
            color="primary"
          />
        </v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title class="pr-4">
            Copy
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>


      <v-menu
        v-model="show_instance_template_menu"
        :attach="true"
        :close-on-click="false"
        :close-on-content-click="false"
      >
        <v-card>
          <v-card-title>Create Instance Template: </v-card-title>
          <v-card-text>
            Name:
            <v-text-field
                v-model="instance_template_name"
                @focus="$store.commit('set_user_is_typing_or_menu_open', true)"
                @blur="$store.commit('set_user_is_typing_or_menu_open', false)"
                          ></v-text-field>
          </v-card-text>
          <v-card-actions>
            <v-btn @click="show_instance_template_menu = false,
                           $store.commit('set_user_is_typing_or_menu_open', false)">Close</v-btn>
            <v-btn @click="create_instance_template" color="success">Create Instance Template</v-btn>
          </v-card-actions>
        </v-card>
      </v-menu>


      <v-list-item
        link
        dense
        data-cy="create_instance_template"
        v-if="instance_hover_index_locked != null"
        @click="on_click_create_instance_template"
      >
        <v-list-item-icon>
          <tooltip_icon
            tooltip_message="Create Instance Template"
            icon="mdi-shape-plus"
            color="primary"
          />
        </v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title class="pr-4">
            Create Template
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>

      <v-list-item
        link
        dense
        data-cy="delete_instance"
        v-if="polygon_point_hover_locked"
        @click="on_click_delete_polygon_point"
      >

        <v-list-item-icon>
          <tooltip_icon

            tooltip_message="Delete Instance"
            icon="mdi-vector-polyline-minus"
            color="primary"
          />
        </v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title class="pr-4">
            Delete Polygon Point
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
      <v-list-item
        link
        dense
        data-cy="delete_instance"
        v-if="instance_hover_index_locked != undefined"
        @click="on_click_delete_instance"
      >

        <v-list-item-icon>
          <tooltip_icon
            tooltip_message="Delete Instance"
            icon="delete"
            color="primary"
          />
        </v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title class="pr-4">
            Delete
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
      <v-list-item
        link
        dense
        data-cy="share_instance"
        v-if="instance_hover_index_locked != undefined"
        @click="show_share_context_menu"
      >
        <v-list-item-icon>
          <tooltip_icon
            tooltip_message="Share"
            icon="share"
            color="primary"
          />
        </v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title class="pr-4">
            Share
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>

      <v-list-item
        link
        dense
        data-cy="instance_history"
        v-if="instance_hover_index_locked != undefined"
        @click="show_instance_history_panel"
      >
        <v-list-item-icon>
          <tooltip_icon
            tooltip_message="Show Instance History"
            icon="mdi-history"
            color="primary"
          />
        </v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title class="pr-4">
            History
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>



      <v-list-item
        link
        dense
        @click="open_issue_panel"
      >
        <v-list-item-icon>
          <tooltip_icon
            tooltip_message="Create Issue"
            icon="mdi-alert-circle"
            color="primary"
          />
        </v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title class="pr-4">
            Create Issue
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>


      <v-divider></v-divider>

      <v-list-item
        v-if="instance_hover_index_locked != undefined"
        dense
      >
        <v-list-item-icon>
          <tooltip_icon
            tooltip_message="Source"
            icon="mdi-file-question"
            color="primary"
          />
        </v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title class="pr-4">
            Source: {{ selected_instance.change_source }}
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>


      <v-list-item
        v-if="instance_hover_index_locked != undefined &&
              selected_instance.created_time"
        dense
      >
        <v-list-item-icon>
          <tooltip_icon
            tooltip_message="Version & Created"
            icon="mdi-clock-outline"
            color="primary"
          />
        </v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title class="pr-4">
            #{{ selected_instance.version }} @
            {{selected_instance.created_time | moment("M-DD-YY H:mm:ss a")}}
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>


      <v-list-item
        dense
        v-if="instance_hover_index_locked != undefined &&
              member && member.first_name"
                   >
      <v-list-item-icon>
        <user_icon
          :size="25"
          class="pb-2"
          :user="member"/>
      </v-list-item-icon>

        <v-list-item-content>
          <v-list-item-title class="pr-4">
              By: {{member.first_name}} {{member.last_name}}
          </v-list-item-title>
        </v-list-item-content>

      </v-list-item>


    </v-card>
    <share_instance_dialog :show_share_instance_menu="show_share_instance_menu"
                           :project_string_id="project_string_id"
                           @share_dialog_close="close_share_dialog"


    ></share_instance_dialog>

  </div>

</template>
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
