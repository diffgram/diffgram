<template>
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

    <v-snackbar
        v-model="show_schema_editing_snackbar"
        :multi-line="true"
        :timeout="-1"
        right
        top
      >
      <b>Editing UI Design</b> <br>
      Hover over a button to show options. Click plus to add buttons.

      <template v-slot:action="{ attrs }">

        <v-text-field
          v-if="edit_name == true"
          v-model="$store.state.ui_schema.current.name"
          @input="has_changes = true"
          @focus="$store.commit('set_user_is_typing_or_menu_open', true)"
          @blur="$store.commit('set_user_is_typing_or_menu_open', false)"
          flat
            >
        </v-text-field>

        <!--
        <userscript_select
          :project_string_id="project_string_id"
          @change="change_userscript($event)"
          :current_userscript_prop="userscript_literal"
          :disabled="userscript_select_disabled"
                        >
        </userscript_select>
        -->

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
            @click="copy_ui_schema_with_servercall(ui_schema_literal)"
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
                  || public_script_not_super_admin"
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
                      || public_script_not_super_admin"
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

<script lang="ts">

  import Vue from 'vue';
  import axios from 'axios';
  import {UI_Schema} from './ui_schema'

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
      'show_save' :{
        default: true
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

        edit_name: false,
        loading: false,
        error: {},

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
        return this.$store.state.ui_schema.current
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

            console.log(result)

            this.userscript_literal.id = result.data.userscript.id;
            this.userscript_literal.time_created = result.data.userscript.time_created;

            // eg for script changes etc as that grows
            this.change_userscript(this.userscript_literal)

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
      update_userscript_with_servercall: async function(){

        //console.debug(this.userscript_literal)
        if (!this.userscript_literal || !this.userscript_literal.id) { return }

        this.loading = true;
        this.error = {}

        try{
          const result = await axios.post(
            `/api/v1/project/${this.project_string_id}/userscript/update`,
            this.userscript_literal
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
      
      toggle_is_visible: async function () {

        this.userscript_literal.is_visible = !this.userscript_literal.is_visible
        this.update_userscript_with_servercall()

      },

      toggle_is_archive: async function () {

        this.userscript_literal.archived = !this.userscript_literal.archived
        this.update_userscript_with_servercall()

      },

      toggle_is_public: async function () {

        // requires super admin
        this.userscript_literal.is_public = !this.userscript_literal.is_public
        this.update_userscript_with_servercall()

      },

      copy_ui_schema_with_servercall: async function(){

        this.ui_schema_literal = this.userscript_class.copy_userscript(
            this.userscript_literal)

        this.loading = true;
        this.error = {}

        try{
          const result = await axios.post(
            `/api/v1/project/${this.project_string_id}/userscript/new`,
            this.userscript_literal
          )
          if(result.status === 200){
            this.userscript_literal.id = result.data.userscript.id;
            this.userscript_literal.time_created = result.data.userscript.time_created;

            // eg for script changes etc as that grows
            this.change_userscript(this.userscript_literal)

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
    z-index: 100;
  }

  .context-menu.visible {
    display: block;
  }
</style>
