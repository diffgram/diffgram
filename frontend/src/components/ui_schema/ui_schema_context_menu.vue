<template>
<div>
  <div
    class="context-menu"
    :class="{visible: show_context_menu}"
    :style="{top: top, left: left}"
  >

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

  </div>

  <div
      class="save-menu"
      :class="{visible: show_context_menu}"
      :style="{top: 0, right: 0}"
    >

    <v-card>
      <v-card-title>Editing UI</v-card-title>

      <v-alert
            type="info"
            dismissible>
        <b>Editing UI Design</b> <br>
        Hover over a button to show options. Click plus to add buttons.
      </v-alert>

      <v-container>
      <v-layout>

        <v_error_multiple :error="error">
        </v_error_multiple>
      
        <ui_schema_selector
          :project_string_id="project_string_id"
          @change="change($event)"
          :current_ui_schema_prop="$store.state.ui_schema.current"
          :disabled="selector_disabled"
                        >
        </ui_schema_selector>
      
        <v-text-field
          v-if="edit_name == true"
          v-model="$store.state.ui_schema.current.name"
          @input="has_changes = true"
          @focus="$store.commit('set_user_is_typing_or_menu_open', true)"
          @blur="$store.commit('set_user_is_typing_or_menu_open', false)"
          flat
            >
        </v-text-field>

        <tooltip_button
            tooltip_message="Edit Name"
            datacy="ui_schema_edit_name"
            @click="edit_name = !edit_name"
            icon="edit"
            :icon_style="true"
            color="primary"
            :disabled="!$store.state.ui_schema.current"
                        >
        </tooltip_button>

        <tooltip_button
            tooltip_message="New"
            datacy="ui_schema_new"
            @click="new_ui_schema_with_servercall()"
            icon="add"
            :icon_style="true"
            color="primary"
                        >
        </tooltip_button>

        <tooltip_button
            tooltip_message="Copy to New"
            datacy="ui_schema_copy"
            @click="copy_ui_schema_with_servercall()"
            icon="mdi-content-copy"
            :icon_style="true"
            color="primary"
            :disabled="!ui_schema_exists"
                        >
        </tooltip_button>


        <tooltip_button
          v-if="show_save"
          datacy="ui_schema_save"
          tooltip_message="Save ui_schema"
          @click="update_ui_schema_with_servercall()"
          icon="save"
          :loading="loading"
          :disabled="loading
                  || !ui_schema_exists
                  || public_not_super_admin"
          :icon_style="true"
          color="primary"
                      >
      </tooltip_button>

      <tooltip_button
          v-if="$store.state.user.current.is_super_admin == true"
          tooltip_message="Toggle is Public Example"
          @click="toggle_is_public()"
          icon="mdi-earth"
          :icon_style="true"
          color="primary"
                      >
      </tooltip_button>

        <div  v-if="$store.state.user.current.is_super_admin == true">
            <div v-if="$store.state.ui_schema.current.is_public">
                Public
            </div> <div v-else>
                Not Public
            </div>
        </div>

      <tooltip_button
          v-if="!$store.state.ui_schema.current.archived"
          tooltip_message="Archive"
          @click="toggle_is_archive()"
          icon="archive"
          :icon_style="true"
          color="primary"
          :disabled="!ui_schema_exists
                    || public_not_super_admin"
                      >
      </tooltip_button>


      <tooltip_button
          v-if="$store.state.ui_schema.current.archived"
          tooltip_message="Restore"
          @click="toggle_is_archive()"
          icon="mdi-delete-restore"
          :icon_style="true"
          color="primary"                          >
      </tooltip_button>


      <tooltip_button
          tooltip_message="Restore Defaults"
          @click="reset()"
          icon="mdi-restore "
          :icon_style="true"
          color="primary"                          >
      </tooltip_button>

      <v-btn
        color="red"
        text
        @click="close()"
      >
        Exit
      </v-btn>
    </v-layout>
      </v-container>
    </v-card>
  </div>

</div>

</template>

<script lang="ts">

  import Vue from 'vue';
  import axios from 'axios';
  import {UI_Schema} from './ui_schema'
  import ui_schema_selector from './ui_schema_selector'

  export default Vue.extend({
    name: 'UI_Schema_context_menu',
    components: {
      ui_schema_selector
    },
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
      'show_save' :{
        default: true
      },

    },
    data() {
      // move context menu off the page out of view when hidden
      return {
        selector_disabled: false,

        top: '-1000px',
        left: '-1000px',
        instance_hover_index_locked: null,
        show_share_instance_menu: false,
        locked_mouse_position: undefined,
        show_add_menu: false,
        show_schema_editing_snackbar: true,

        edit_name: false,
        loading: false,
        error: {},

        button_to_add: undefined,

        buttons_list_original: [
            {'name': 'previous_task',
             'display_name': 'Previous Task',
             'icon': 'mdi-chevron-left-circle',
             'color': 'primary'
            },
            {'name': 'next_task',
             'display_name': 'Next Task',
             'icon': 'mdi-chevron-right-circle',
             'color': 'primary'
            },
            {'name': 'logo',
             'display_name': 'Logo',
             'image-icon': 'https://res-4.cloudinary.com/crunchbase-production/image/upload/c_lpad,h_25,w_25,f_auto,b_white,q_auto:eco/okhxici7vjqqznihxezz',
            },
            {'name': 'home_button',
             'icon': 'mdi-home',
             'display_name': 'Home Button',
            },
            {'name': 'defer',
             'icon': 'mdi-debug-step-over',
             'display_name': 'Defer',
            },
            {'name': 'zoom',
             'icon': 'mdi-magnify-plus-outline',
             'display_name': 'Zoom Display',
            },
            {'name': 'label_selector',
             'icon': 'mdi-format-paint',
             'display_name': 'Label Selector',
            },
            {'name': 'instance_selector',
             'icon': 'mdi-vector-polygon',
             'display_name': 'Tool Selector',
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
      ui_schema_exists: function () {
           if (this.get_ui_schema().client_created_time ||   // frontend
               this.get_ui_schema().id) { // backend
               return true
           }
       },
      public_not_super_admin: function () {
           if (this.$store.state.ui_schema.current.is_public == true
            && this.$store.state.user.current.is_super_admin != true) {
               return true
           }
       }

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
      get_ui_schema: function () {
        if (this.$store.state.ui_schema.current == undefined) {
          throw new Error("this.$store.state.ui_schema.current is undefined")
        }
        return this.$store.state.ui_schema.current
      },
      get_target_element: function () {
        // careful target is stored on ui_schema generally not `current`
        return this.$store.state.ui_schema.target_element
      },
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
        this.$store.commit('set_ui_schema_element_value',
          [this.get_target_element(),'visible', false])
        //this.close();
      },
      show() {
        this.$store.commit('set_ui_schema_element_value',
          [this.get_target_element(),'visible', true])
        //this.close();
      },
      add_selected() {
        this.$store.commit('set_ui_schema_element_value',
          [this.button_to_add,'visible', true])
      },

      new_ui_schema_with_servercall: async function(){


        let ui_schema = new UI_Schema
        ui_schema.new()
        console.log(ui_schema)

        this.loading = true;
        this.error = {}

        try{
          const result = await axios.post(
            `/api/v1/project/${this.project_string_id}/ui_schema/new`,
            ui_schema.serialize()
          )
          if(result.status === 200){

            this.change(result.data.ui_schema)
            this.edit_name = true // assume a user wants to edit name of new script
          }

        }
        catch (error) {
          this.error = this.$route_api_errors(error)
          console.error(error)

        }
        finally {
          this.loading = false;
        }

      },
      update_ui_schema_with_servercall: async function(){

        if (!this.get_ui_schema() || !this.get_ui_schema().id) { return }

        this.loading = true;
        this.error = {}

        try{
          const result = await axios.post(
            `/api/v1/project/${this.project_string_id}/ui_schema/update`,
            this.get_ui_schema()
          )

        }
        catch (error) {
          this.error = this.$route_api_errors(error)
          console.error(error)

        }
        finally {
          this.loading = false;
        }

      },

      change: function (event) {

        if(!event) { return }
        if(event.id == this.$store.state.ui_schema.current.id) { return }
       
        this.$store.commit('set_ui_schema', event)

      },
      
      toggle_is_visible: async function () {

        this.$store.commit('set_ui_schema_top_level_key_value',
          ['is_visible', !this.get_ui_schema().is_visible])
        this.update_ui_schema_with_servercall()

      },

      toggle_is_archive: async function () {

        this.$store.commit('set_ui_schema_top_level_key_value',
          ['archived', !this.get_ui_schema().archived])
        this.update_ui_schema_with_servercall()

      },

      toggle_is_public: async function () {

        // requires super admin
        this.$store.commit('set_ui_schema_top_level_key_value',
          ['is_public', !this.get_ui_schema().is_public])
        this.update_ui_schema_with_servercall()

      },

      copy_ui_schema_with_servercall: async function(){

        let ui_schema = new UI_Schema
        const new_ui_schema = ui_schema.copy(this.get_ui_schema())

        this.loading = true;
        this.error = {}

        try{
          const result = await axios.post(
            `/api/v1/project/${this.project_string_id}/userscript/new`,
            new_ui_schema
          )
          if(result.status === 200){

            this.change(result.data.ui_schema)
            this.edit_name = true // assume a user wants to edit name of new script
          }
        }
        catch (error) {
          this.error = this.$route_api_errors(error)
          console.error(error)
        }
        finally {
          this.loading = false;
        }
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
    z-index: 10000;
  }

  .save-menu {
    position: absolute;
    margin: 0;
    box-sizing: border-box;
    display: none;
    z-index: 1000;
  }

  .context-menu.visible {
    display: block;
  }
  .save-menu.visible {
    display: block;
  }
</style>
