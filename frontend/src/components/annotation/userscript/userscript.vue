<template>
  <div ref="userscript"
       v-cloak
       >

      <v-text-field
          v-if="edit_name == true"
          v-model="userscript_literal.name"
          @input="has_changes = true"
          @focus="$store.commit('set_user_is_typing_or_menu_open', true)"
          @blur="$store.commit('set_user_is_typing_or_menu_open', false)"
          flat
          >
      </v-text-field>

      <v-layout>

        <userscript_select
              :project_string_id="project_string_id"
              @change="change_userscript($event)"
              :current_userscript_prop="userscript_literal"
              :disabled="userscript_select_disabled"
                           >
        </userscript_select>

        <div class="pa-1"
             v-if="show_other_controls">
          <v-layout>

            <tooltip_button
                tooltip_message="Edit Name"
                datacy="userscript_edit_name"
                @click="edit_name = !edit_name"
                icon="edit"
                :icon_style="true"
                color="primary"
                :disabled="!userscript_exists"
                            >
            </tooltip_button>

            <tooltip_button
                tooltip_message="New"
                datacy="userscript_new"
                @click="new_userscript_with_servercall()"
                icon="add"
                :icon_style="true"
                color="primary"
                            >
            </tooltip_button>

            <tooltip_button
                tooltip_message="Copy to New"
                datacy="userscript_copy"
                @click="copy_userscript_with_servercall(userscript_literal)"
                icon="mdi-content-copy"
                :icon_style="true"
                color="primary"
                :disabled="!userscript_exists"
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
                <div v-if="userscript_literal.is_public">
                    Public
                </div> <div v-else>
                    Not Public
                </div>
            </div>

          </v-layout>
        </div>

      </v-layout>

      <v-layout class="pb-4">

        <tooltip_button
            tooltip_message="Run (Q)"
            datacy="userscript_run"
            @click="run_users_script()"
            icon="mdi-play"
            :icon_style="true"
            color="primary"
            :disabled="!play_ready"
                        >
        </tooltip_button>

        <tooltip_button
            tooltip_message="Watch"
            @click="parse_watcher()"
            icon="mdi-clock"
            :icon_style="true"
            color="primary"
            :disabled="!userscript_exists"
                        >
        </tooltip_button>

        <tooltip_button
            v-if="show_save"
            datacy="userscript_save"
            tooltip_message="Save UserScript"
            @click="update_userscript_with_servercall()"
            icon="save"
            :loading="loading"
            :disabled="loading
                    || !userscript_exists
                    || public_script_not_super_admin"
            :icon_style="true"
            color="primary"
                        >
        </tooltip_button>


        <!--
        The idea of this was if annotators can choose from a list of scripts
        engineer may want to choose to make it visible or not etc.

        However, for V1 engineer may choose single script for specific task
        So this visibility thing is not really clear - so hide for now.
          -->
        <!--
            <div v-if="show_other_controls">
              <tooltip_button
                  v-if="userscript_literal.is_visible"
                  tooltip_message="Is Visible. Select to Hide From Annotators"
                  @click="toggle_is_visible()"
                  icon="mdi-eye"
                  :icon_style="true"
                  color="primary"
                  :disabled="!userscript_exists"
                              >
              </tooltip_button>

              <tooltip_button
                  v-if="!userscript_literal.is_visible"
                  tooltip_message="Is Hidden. Select to Publish to Annotators"
                  @click="toggle_is_visible()"
                  icon="mdi-eye-off"
                  :icon_style="true"
                  color="primary"
                  :disabled="!userscript_exists"
                              >
              </tooltip_button>
            </div>
        -->

        <div v-if="show_other_controls">
          <tooltip_button
              v-if="!userscript_literal.archived"
              tooltip_message="Archive"
              @click="toggle_is_archive()"
              icon="archive"
              :icon_style="true"
              color="primary"
              :disabled="!userscript_exists
                       || public_script_not_super_admin"
                          >
          </tooltip_button>


          <tooltip_button
              v-if="userscript_literal.archived"
              tooltip_message="Restore"
              @click="toggle_is_archive()"
              icon="mdi-delete-restore"
              :icon_style="true"
              color="primary"                          >
          </tooltip_button>
        </div>

        <div v-if="show_external_scripts">
          <tooltip_button
            tooltip_message="Add External Scripts"
            @click="userscript_sources_selector_dialog_is_open = true"
            icon="mdi-npm"
            :icon_style="true"
            :bottom="true"
            color="primary"
            :disabled="!userscript_exists"
          >
          </tooltip_button>

          <regular_chip
              v-if="userscript_literal.external_src_list"
              @click="userscript_sources_selector_dialog_is_open = true"
              :message="userscript_literal.external_src_list.length"
              tooltip_message="External Scripts"
              color="primary"
              tooltip_direction="bottom"
              :small="true">
          </regular_chip>
        </div>

        <v-layout v-if="userscript_class"
                  class="pa-1">
          <tooltip_icon
              v-if="userscript_class.status_loaded_scripts"
              tooltip_message="Loaded Scripts"
              icon="mdi-check"
              color="primary"
              class="pa-2"
                        >
          </tooltip_icon>

          <tooltip_icon
              v-if="userscript_class.status_loaded_watchers"
              tooltip_message="Loaded Watchers"
              icon="mdi-check-all"
              color="primary"
              class="pa-2"
                        >
          </tooltip_icon>

          <div v-if="userscript_class.status_loaded_scripts">
            <div v-if="userscript_class.running">
                <v-chip
                    color="green"
                    text-color="white"
                              >
                    Running
                </v-chip>
            </div>
            <div v-else>
                <v-chip
                    color="primary"
                              >
                    Ready
                </v-chip>
            </div>
          </div>


           {{userscript_class.run_time}}


          <v-progress-linear
          :active="userscript_class.running"
          height="5"
          indeterminate
          absolute
          top
          color="primary accent-4">
          </v-progress-linear>

        </v-layout>

      </v-layout>


  <v-dialog v-model="userscript_sources_selector_dialog_is_open"
            max-width="1500px"
            id="userscript_sources_selector-dialog">
    <v-card elevation="0">

      <userscript_sources_selector
          :project_string_id="project_string_id"
          :userscript="userscript_literal"
          @add="userscript_literal.external_src_list.push($event)"
          @remove="userscript_literal.external_src_list.splice($event, 1)"
                                    >
      </userscript_sources_selector>

    </v-card>
  </v-dialog>

    <v_error_multiple :error="error">
     </v_error_multiple>

    <div v-if="userscript_class">
      <v-alert v-if="userscript_class.error_construction ||
                     userscript_class.error_runtime"
               type="error"
               dismissible>

        (Line: {{userscript_class.error_line}})

        {{userscript_class.error_construction}}
        {{userscript_class.error_runtime}}

      </v-alert>

      <!-- Hide while WIP -->
      <!--
      {{userscript_class.logMessages}}
      -->

    </div>

      <!-- We assume if there is no script selected we don't show editor because
           otherwise confusing if user starts to enter code -->

      <codemirror v-if="show_code_editor == true
                    && userscript_exists"
                  ref="userscript_editor"
                  v-model="userscript_literal.code"
                  :options="cmOptions"
                  @focus="$store.commit('set_user_is_typing_or_menu_open', true)"
                  @blur="$store.commit('set_user_is_typing_or_menu_open', false)"
                  :width="userscript_editor_width"
                  :height="userscript_editor_height"
                  >
      </codemirror>





    </div>
</template>

<script>

import {UserScript} from './userscript.ts'
import Vue from "vue";
import axios from 'axios';


import codemirror from './codemirror.vue'
import userscript_select from './userscript_select.vue'
import userscript_sources_selector from './userscript_sources_selector.vue'

  export default Vue.extend( {
    name: "userscript",
    components : {
      codemirror,
      userscript_select,
      userscript_sources_selector
    },
    props:{
      'project_string_id_prop':{
        default: null
      },
      'create_instance':{
        default: null
      },
      'current_userscript_prop':{
        default: null
      },
      'userscript_select_disabled' :{
        default: false
      },
      'show_code_editor' :{
        default: true
      },
      'show_save' :{
        default: true
      },
      'show_external_scripts': {
        default: true
      },
      'show_other_controls' : {
        default: true
      }
    },

    data() {
      return {

        changing_userscript: false,

        userscript_editor_width: null,
        userscript_editor_height: null,

        edit_name: false,
        userscript_sources_selector_dialog_is_open: false,

        has_changes: false,

        cmOptions: {
          tabSize: 4,
          mode: 'javascript',
          lineNumbers: true,
          line: true
          // more CodeMirror options...
        },

        loading: false,
        error: {},

        userscript_literal: {},
        project_string_id: null,
        userscript_class: null,

        // check userscript.ts for class this is view focused

      }
    },

    watch: {
      userscript_sources_selector_dialog_is_open: function () {
        if (!this.userscript_literal) {
          return
        }
        this.userscript_class.remove_old_add_new(
          this.userscript_literal.external_src_list)
      },
      create_instance: function (instance) {

        this.userscript_class.run_event(instance)

      },
      current_userscript_prop: function (userscript) {
        this.change_userscript(userscript)
      }
    },
    computed:{
       play_ready: function () {
            if (!this.userscript_literal.code) {
                return false
            }
            if (!this.userscript_class) {
                return false
            }
            if (this.userscript_class.external_src_list
              && this.userscript_class.external_src_list.length > 0
              && !this.userscript_class.status_loaded_scripts) {
                return false
            }
            if (this.userscript_class.running) {
                return false
            }
            return true
        },

       userscript_exists: function () {
           if (this.userscript_literal.client_created_time ||   // frontend
               this.userscript_literal.id) {        // backend
               return true
           }
       },

       public_script_not_super_admin: function () {
           if (this.userscript_literal.is_public == true
            && this.$store.state.user.current.is_super_admin != true) {
               return true
           }
       }
    },

    created: function () {

      this.userscript_editor_width = 600
      this.userscript_editor_height = 600

      if (!this.project_string_id_prop) {
        this.project_string_id = this.$store.state.project.current.project_string_id
      } else {
        this.project_string_id = this.project_string_id_prop
      }

    },

    mounted: function () {

      this.userscript_class = new UserScript()

      this.change_userscript(this.$props.current_userscript_prop)

      window.addEventListener('keydown', this.hotkeys);
      //this.add_script_multiple(this.custom_script_list)


    },
    methods: {


    hotkeys: function (event) {
        if (this.$store.state.user.is_typing_or_menu_open == true) {
            return
        }
        if (event.key === 'q') {
            this.run_users_script()
        }
        if (event.key === 's'
          && event.ctrlKey == true) {

            event.preventDefault()

            this.update_userscript_with_servercall()
        }

     },

      change_userscript: function (event) {

        if(!event) { return }
        if(event.id == this.userscript_literal.id) { return }
        if(this.changing_userscript == true) { return }
        this.changing_userscript = true

        this.userscript_literal = event

        let allowed_scripts = this.userscript_literal.external_src_list
        let result_bool = this.userscript_class.remove_old_add_new(allowed_scripts)


        // if we can make the userscript literal an instance of the class we can avoid this
        this.userscript_class.reset_shared()

        this.changing_userscript = false

      },

      // WINDOW LEVEL APPROACH
      run_users_script: function() {

        let context = "document.querySelector('#annotation_core').__vue__"

        // Main
        this.userscript_class.build_and_run(this.userscript_literal.code, context)

      },

      // seperate as a hack until parsing is better
      parse_watcher: function() {

        let context = "document.querySelector('#annotation_core').__vue__"
        this.userscript_class.parse_high_level_into_functions(this.userscript_literal.code, context)


      },

      copy_userscript_with_servercall: async function(){

        this.userscript_literal = this.userscript_class.copy_userscript(
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



      new_userscript_with_servercall: async function(){

        this.userscript_literal = this.userscript_class.new_userscript()

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


    },

    beforeDestroy() {
        window.removeEventListener('keyup', this.hotkeys)
    }
  })
</script>

