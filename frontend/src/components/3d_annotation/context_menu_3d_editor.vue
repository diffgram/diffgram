<template>
  <div
    class="context-menu"
    :class="{visible: show_context_menu}"
    :style="{top: top, left: left}"
  >
    <!-- Instance context -->
    <v-card
      class="ma-auto"
      max-width="300"
      tile>
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
                           @click:outside="close_share_dialog()"

    ></share_instance_dialog>

  </div>

</template>
<script lang="ts">
  import Vue from 'vue';
  import axios from 'axios';
  import share_instance_dialog from '../share/share_instance_dialog';
  import user_icon from '../../components/user/user_icon'

  export default Vue.extend({
    name: 'context_menu_3d_editor',
    components: {
      share_instance_dialog,
      user_icon
    },
    props: {
      'mouse_position': {
        type: Object,
        default: null,
      },
      'task': {
        type: Object,
        default: null,

      },
      'draw_mode': {
        type: Boolean,
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
      'hovered_figure_id': {
        type: String,
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
        hovered_figure_id_locked: null,
        instance_index_to_paste: null,
        show_share_instance_menu: false,
        x: 0,
        y: 0,
        num_frames: 1,
        locked_mouse_position: undefined,
      }
    },

    computed: {
      selected_instance: function () {
        let selected = this.instance_list[this.instance_hover_index_locked]
        if (selected) {
          return selected
        } else {
          return {}
        }
      },
      member: function () {
        return this.$store.state.project.current.member_list.find(x => {
          let instance = this.instance_list[this.instance_hover_index_locked]
          if(instance){
            return x.member_id == instance.member_created_id
          }
          return false;

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
          this.hovered_figure_id_locked = this.hovered_figure_id;
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

    },
    methods: {

      show_instance_history_panel: function () {
        this.$emit('open_instance_history_panel', this.instance_hover_index_locked);
      },
      close_instance_history_panel: function () {
        this.$emit('close_instance_history_panel', this.instance_hover_index_locked);
      },

      close() {
        this.$emit('close_context_menu');
        this.$store.commit('set_user_is_typing_or_menu_open', false)
      },

      get_mouse_position: function () {
        this.top = this.mouse_position.screen_y + 'px';
        this.left = this.mouse_position.screen_x + 'px';
        this.locked_mouse_position = {...this.mouse_position};
      },

      on_click_delete_instance() {
        this.$emit('delete_instance', this.instance_hover_index_locked)
      },
      show_share_context_menu() {
        this.show_share_instance_menu = true;
        this.$store.commit('set_user_is_typing_or_menu_open', true);
        this.$emit('share_dialog_open');

      },
      on_click_copy_instance() {
        this.$emit('copy_instance', this.instance_hover_index_locked);
        this.close();
      },
      open_issue_panel: function(){
        this.$emit('open_issue_panel')
      },
      on_click_paste_instance() {
        this.$emit('paste_instance');
        this.close();
      },
      close_share_dialog() {
        this.show_share_instance_menu = false;
        this.$store.commit('set_user_is_typing_or_menu_open', false);
        this.$emit('share_dialog_close')

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
