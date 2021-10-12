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
        show_schema_editing_snackbar: true,

        button_to_add: undefined,

        buttons_list_original: [
            {'name': 'show_previous_task',
             'display_name': 'Previous Task',
             'icon': 'mdi-chevron-left-circle',
             'color': 'primary'
            },
            {'name': 'show_next_task',
             'display_name': 'Next Task',
             'icon': 'mdi-chevron-right-circle',
             'color': 'primary'
            },
            {'name': 'show_logo',
             'display_name': 'Logo',
             'image-icon': 'https://res-4.cloudinary.com/crunchbase-production/image/upload/c_lpad,h_25,w_25,f_auto,b_white,q_auto:eco/okhxici7vjqqznihxezz',
            },
            {'name': 'show_home_button',
             'icon': 'mdi-home',
             'display_name': 'Home Button',
            },
            {'name': 'show_defer',
             'icon': 'mdi-debug-step-over',
             'display_name': 'Defer',
            },
            {'name': 'show_zoom',
             'icon': 'mdi-magnify-plus-outline',
             'display_name': 'Zoom Display',
            },
            {'name': 'show_label_selector',
             'icon': 'mdi-format-paint',
             'display_name': 'Label Selector',
            },
            {'name': 'show_instance_selector',
             'icon': 'mdi-vector-polygon',
             'display_name': 'Label Selector',
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
      this.show_ui_schema_add_menu = this.$store.watch((state) => {
          return this.$store.state.ui_schema.ui_schema_add_menu
        },
        (new_val, old_val) => {
          this.show_add_menu = new_val
        },
      )
      // OR worst case can watch the refresh value of ui_schema
    },
    beforeDestroy() {
      this.get_target_element_watcher()
      this.show_ui_schema_add_menu()
    },
    methods: {
      get_mouse_position: function () {
        if (!this.$store.state.ui_schema.target_element) {
          // we don't update mouse position unless exiting the edit mode
          this.show_add_menu = false
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
      reset(){
        this.$store.commit('reset_ui_schema')
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
        v-if="$store.state.ui_schema.target_element != 'add_button'"
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
            icon="add"
            color="primary"
          />
        </v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title class="pr-4">
            Add
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>

      <v-list-item
        link
        @click="close()"
      >

        <v-list-item-icon>
          <tooltip_icon
            tooltip_message="Exit"
            icon="close"
            color="primary"
          />
        </v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title class="pr-4">
            Exit
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

    <v-snackbar
        v-model="show_schema_editing_snackbar"
        :multi-line="true"
        :timeout="-1"
        right
      >
        <b>Editing UI Design</b> <br>
        Hover over a button to show options. Click plus to add buttons.

        <template v-slot:action="{ attrs }">
          <v-btn
            color="white"
            text
            v-bind="attrs"
            @click="reset()"
          >
          <v-icon left > mdi-restore </v-icon>
            Reset
          </v-btn>

          <v-btn
            color="red"
            text
            v-bind="attrs"
            @click="close()"
          >
            Exit
          </v-btn>
        </template>
      </v-snackbar>

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
