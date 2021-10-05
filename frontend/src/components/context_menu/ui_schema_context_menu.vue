<script lang="ts">
  import Vue from 'vue';
  import axios from 'axios';
  export default Vue.extend({
    name: 'UI_Schema_context_menu',
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
        default: true   // temporary true, false when done
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
        show_add_menu: false,

        button_to_add: undefined,

        buttons_list_original: [
            {'name': 'previous_task',
             'display_name': 'Previous Task',
             'icon': 'mdi-chevron-left-circle',
             'color': 'primary'
            },
            {'name': 'failed',
              'icon': 'error'
            },
            {'name': 'processing',
              'icon': ''
            }
          ]
      }
    },

    computed: {
      buttons_list_available: function () {
        let list = []
        for (var button of this.buttons_list_original) {
          if (this.$store.getters.get_ui_schema(button.name) != true) {
            list.push(button)
          }
        }
        return list
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
    mounted() {
      var self = this
      this.get_target_element_watcher = this.$store.watch((state) => {
          return this.$store.state.ui_schema.target_element
        },
        (new_val, old_val) => {
          self.get_mouse_position()
        },
      )
      // OR worst case can watch the refresh value of ui_schema
    },
    beforeDestroy() {
      this.get_target_element_watcher()
    },
    methods: {
      get_mouse_position: function () {
        if (!this.$store.state.ui_schema.target_element) {
          // we don't update mouse position unless exiting the edit mode
          return
        }
        let event = this.$store.state.ui_schema.event
        console.log(event)
        this.top = event.clientY - event.offsetY + 'px';
        this.left = event.clientX - event.offsetX + 'px';
        //this.locked_mouse_position = {...this.mouse_position};
      },
      close(){
        this.$emit('close_context_menu')
      },
      hide() {
        this.$store.commit('set_ui_schema_element_value', false)
        //this.close();
      },
      show() {
        this.$store.commit('set_ui_schema_element_value', true)
        //this.close();
      },
      add_selected() {
        this.$store.commit('set_ui_schema_element_target_and_value',
          [this.button_to_add, true])
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


      <v-list-item
        link
        @click="hide"
      >

        <v-list-item-icon>
          <tooltip_icon
            tooltip_message="Hide"
            icon="mdi-eye-off"
            color="primary"
          />
        </v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title class="pr-4">
            Hide
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>

      <v-list-item
        link
        @click="show_add_menu = true"
      >

        <v-list-item-icon>
          <tooltip_icon
            tooltip_message="Show"
            icon="mdi-eye"
            color="primary"
          />
        </v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title class="pr-4">
            Add
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>

      <v-menu

        v-model="show_add_menu"
        :allow-overflow="true"
        :offset-overflow="true"
        :close-on-click="false"
        :close-on-content-click="false"
        :attach="true"
        :z-index="999999"
      >
        <v-card>
          <v-card-title>Add</v-card-title>
          <v-card-text>

            <diffgram_select
                :item_list="buttons_list_available"
                v-model="button_to_add"
                label="Buttons"
                >
            </diffgram_select>

          </v-card-text>
          <v-card-actions>
            <v-btn @click="show_add_menu = false">Close
            </v-btn>
            <v-btn data-cy="add_selected"
                   @click="add_selected"
                   color="success">
              Add Selected
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-menu>


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
