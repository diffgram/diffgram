<script lang="ts">
  import Vue from 'vue';
  export default Vue.extend({
    name: 'PolygonBordersContextMenu',
    props: {
      'mouse_position': {
        type: Object,
        default: null,
      },
      'project_string_id':{
        type: String,
        default: null
      },
      'show_context_menu':{
        type: Boolean,
        default: false
      },

    },
    data() {
      // move context menu off the page out of view when hidden
      return {
        top: '-1000px',
        left: '-1000px',
        instance_hover_index_locked: null,
        show_share_instance_menu: false,
        locked_mouse_position: undefined,
        show_issue_panel: false,

      }
    },

    computed: {
      selected_instance: function(){
        return this.instance_list[this.instance_hover_index_locked];
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

        if (isVisible == true) {
          // lock mouse position on click only
          this.get_mouse_position();
          this.instance_hover_index_locked = this.instance_hover_index

          // We want to free condition on null in template so "normalize" it here.
          if (isNaN(this.instance_hover_index_locked)) {
            this.instance_hover_index_locked = null
          }

        } else {

          this.top = '-1000px';
          this.left = '-1000px';
          this.instance_hover_index_locked = null
        }
      },
    },
    methods: {
      get_mouse_position: function () {
        this.top = this.mouse_position.raw.y + 'px';
        this.left = this.mouse_position.raw.x + 'px';
        this.locked_mouse_position = {...this.mouse_position};
      },
      close(){
        this.$emit('close_context_menu')
      },
      on_click_long_path() {
        let instance_update = {
          index: this.instance_hover_index_locked,
          mode: "delete"
        }
        this.$emit('start_auto_bordering', 'long_path')
        this.close();
      },
      on_click_short_path() {
        let instance_update = {
          index: this.instance_hover_index_locked,
          mode: "delete"
        }
        this.$emit('start_auto_bordering', 'short_path')
        this.close();
      },
    }
  });
</script>
<template>
  <div
    class="context-menu"
    :class="{visible: show_context_menu}"
    :style="{top: top, left: left}"
    data-cy="auto_border_path_prompt"
  >
    <!-- Instance context -->
    <v-card

      class="mx-auto"
      max-width="300"
      tile
    >


      <v-list-item
        link
        @click="on_click_short_path"
        data-cy="auto_border_path_prompt_short"
      >

        <v-list-item-icon>
          <tooltip_icon
            tooltip_message="Delete Instance"
            icon="mdi-shape-polygon-plus"
            color="primary"
          />
        </v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title class="pr-4">
            Short Path
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
      <v-list-item
        link
        @click="on_click_long_path"
      >

        <v-list-item-icon>
          <tooltip_icon
            tooltip_message="Delete Instance"
            icon="mdi-vector-polygon"
            color="primary"
          />
        </v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title class="pr-4">
            Long Path
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>

    </v-card>

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
