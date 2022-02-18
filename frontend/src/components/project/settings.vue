<template>
  <div id="project_settings">

    <v-card>
      <v-container>

        <v-card-title>
          <h1>Settings</h1>
        </v-card-title>

        <v-container>
        <v-card>
          <v-container>

            <v-card-text>

              <v-flex lg4>
                <v-text-field label="Name"
                              v-model="project.name"
                              :rules="[rules.name]">
                </v-text-field>
              </v-flex>

              <v-flex lg4>
                <v-layout>

                  <tooltip_button
                      tooltip_message="Video help"
                      href="https://diffgram.readme.io/docs/video-specifications"
                      icon="help"
                      :icon_style="true"
                      color="primary">
                  </tooltip_button>

                </v-layout>
              </v-flex>

            </v-card-text>
            <v-card-actions>
              <v-btn @click="save"
                     color="primary">
                Save settings
              </v-btn>
            </v-card-actions>

            </v-container>
          </v-card>

        </v-container>


      <v-container>
        <v-card>
          <v-container>

            <h2> Resources </h2>

              <v-btn color="blue darken-1"
                      text
                      @click="$router.push('/project/' + project_string_id + '/attributes')"
                     >
                <v-icon left>mdi-collage</v-icon>
                Attributes
              </v-btn>


          </v-container>
        </v-card>
      </v-container>


      <v-container>

        <v_collaborate_new :project_string_id="project_string_id">
        </v_collaborate_new>

        <v_collaborate_list_existing :project_string_id="project_string_id">
        </v_collaborate_list_existing>

        <v-divider></v-divider>

      </v-container>

        <v-container>
          <v-card>
            <v-container>
              <h2> Danger zone</h2>

              <br />

              <v_info_multiple :info="info">
              </v_info_multiple>

              <v_error_multiple :error="error_multiple">
              </v_error_multiple>

              <v-layout column>


               <!-- Project public start -->
              <v-flex v-if="project.is_public != true">

                <v-alert type="info">
                  Project is private.
                </v-alert>

                <v-dialog v-model="project_public_dialog"
                          >

                  <template v-slot:activator="{ on }">
                    <v-btn color="error"
                           v-on="on">
                      <v-icon left> mdi-earth </v-icon>
                      make public
                    </v-btn>
                  </template>

                  <v-card>
                    <v-container>
                      <v-alert type="warning">

                        The project will be viewable by all users on the public internet.

                      </v-alert>
                      <br />
                      <h2> Type project string id <kbd>{{project_string_id}}</kbd></h2>
                      <v-text-field label="Project string id"
                                    v-model="project_string_id_confirm_public"
                                    :rules="[rules.project_public]">
                      </v-text-field>

                      <v-btn @click="api_project_update('MAKE_PUBLIC')"
                             color="error"
                             :disabled="!project_public_check_passed || api_project_update_loading">
                        Confirm make public
                      </v-btn>

                    </v-container>
                  </v-card>

                </v-dialog>
              </v-flex>
              <!-- Public end -->

              <v-flex v-if="project.is_public == true">

                <v-alert type="warning">
                  Project is public.
                </v-alert>

                <v-btn @click="api_project_update('MAKE_PRIVATE')"
                        color="primary"
                        :disabled="api_project_update_loading">
                  <v-icon left> lock </v-icon>
                  Make private
                </v-btn>
              </v-flex>

              <!-- Shutdown project start -->
                <v-flex>
              <v-dialog v-model="project_delete_dialog"
                        >
                <template v-slot:activator="{ on }">
                  <v-btn color="error"
                         v-on="on">
                    <v-icon left> delete </v-icon>
                    shutdown project
                  </v-btn>
                </template>

                <v-card>
                  <v-container>
                    <v-alert type="warning">

                      The project will be immediately inaccessible.
                      All data associated with the project may be deleted in approximately 30 days.
                    </v-alert>
                    <br />
                    <h2> Type project string id <kbd>{{project_string_id}}</kbd></h2>
                    <v-text-field label="Project string id"
                                  v-model="project_string_id_confirm"
                                  :rules="[rules.project_delete]">
                    </v-text-field>

                    <v-btn @click="api_project_update('DELETE')"
                           color="error"
                           :disabled="!project_delete_check_passed || api_project_update_loading">
                      Confirm shutdown project
                    </v-btn>

                  </v-container>
                </v-card>

              </v-dialog>
                  </v-flex>
              <!-- Shutdown project end -->

              </v-layout>

              </v-container>
          </v-card>
        </v-container>



      </v-container>
    </v-card>

  </div>
</template>

<script lang="ts">
// @ts-nocheck

import axios from '../../services/customAxiosInstance';

import Vue from "vue";
import {create_event} from "../event/create_event";

export default Vue.extend( {
  name: 'project_settings',
  props: ['project_string_id'],
  data () {
    return {
      project: {
        name: null
      },

      project_string_id_confirm: "",

      project_delete_dialog: false,

      error_multiple: {},

      project_public_dialog: false,
      project_string_id_confirm_public: "",

      api_project_update_loading: false,
      project_delete_check_passed: false,

      project_public_check_passed: false,

      info: {},

      rules: {
        required: (value) => !!value || 'Required.',
        name: (value) => {
          const pattern = new RegExp("^[a-zA-Z0-9_ ]{4,30}$")
          return pattern.test(value) || 'No special characters. Between 4 - 30 characters.'
        },
        // TODO share this / make generic?
        project_delete: (value) => {

          if (value != this.project_string_id) {
            this.project_delete_check_passed = false
            return "Must match project string id: " + this.project_string_id
          }
          this.project_delete_check_passed = true
          return true
        },
        project_public: (value) => {

          if (value != this.project_string_id) {
            this.project_public_check_passed = false
            return "Must match project string id: " + this.project_string_id
          }
          this.project_public_check_passed = true
          return true
        },
        fps: (value) => {
          const pattern = new RegExp("^[0-9]{1,3}$")
          return pattern.test(value) || 'Number between 0 and 120, 0 means no fps conversion'
        },
      }
    }
  },
  computed: {
    fan_toggle: function () {
      if (this.project.settings.fan_on == true) {
        return "On"
      } else {
        return "Off"
      }
    }
  },
  created() {
   this.project = this.$store.state.project.current
  },
  mounted(){
    this.add_visit_history_event();
  },
    methods: {
      add_visit_history_event: async function(){
        const event_data = await create_event(this.project_string_id, {
          page_name: 'project_settings',
          object_type: 'page',
          user_visit: 'user_visit',
        })
      },
      get_project: function () {
        this.loading = true
        axios.get('/api/project/view/' + this.project_string_id + '/json')
          .then(response => {
            if (response.data['none_found'] == true) {
              this.none_found = true
            } else {
              this.$store.commit('set_project_name', response.data['project']['name'])
              this.project = response.data.project
              this.checks = response.data.checks

            }
            this.loading = false
          })
          .catch(error => { console.log(error); });
      },
      save: function () {
        this.loading = true
        axios.post('/api/project/' + this.project_string_id + '/update/edit', {
          project : this.project
        })
          .then(response => {

            this.loading = false
            this.$store.commit('set_project', response.data.project)

            // TODO this format needs work
            this.$store.commit('success_message', {'message' : response.data.log.info})



          })
          .catch(error => { console.log(error); });
      },

      api_project_update(mode) {

      this.api_project_update_loading = true
      this.info = {}  // reset

      axios.post('/api/v1/project/' + this.project_string_id
              + '/update',
        {
          'mode': mode
        })
        .then(response => {

          // project is deleted so handle front end stuff

          this.$store.commit('success_message', response.data.log.info)

          if (mode == 'DELETE') {
             this.$store.commit('clear_project')
             this.$router.push('/home/dashboard')
             return
           }

          // Caution this is for update mode
          // assumed delete will return
          this.project = response.data.project
          this.$store.commit('set_project',  this.project)

          this.api_project_update_loading = false
          this.project_public_dialog = false


        }).catch(e => {

          this.error_multiple = e.response.data.log.error

          // not great as we would need this for every one then
          this.project_public_dialog = false

          console.log(e)
          this.api_project_update_loading = false

        })

    }

  }
}
) </script>

