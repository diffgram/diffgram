<template>
  <div id="">

    <v-card>
      <v-container>
        <v-layout column>

          <div v-if="mode == 'NEW' ">
            <v-card-title>
              New Action
            </v-card-title>

            <!-- List of templates -->
            <v-select :items="template_list_valid"
                      v-model="template"
                      label="Template"
                      return-object
                      :disabled="loading"
                      @change="">

              <template v-slot:item="{ item, title }">

                  <v-icon left>
                    {{item.icon}}
                  </v-icon>

                  {{ item.text}}

              </template>

              <template v-slot:selection="{ item, title }">

                  <v-icon left>
                    {{item.icon}}
                  </v-icon>

                  {{ item.text}}

              </template>

            </v-select>
          </div>


          <!-- new_file -->
          <div v-if="template.kind === 'new_file' ">


          </div>

          <div v-if="template.kind === 'count' ">

            <!-- select label file -->
            <label_select_only
             :project_string_id="project_string_id"
              @label_file="recieve_label_file($event)"
                               >
            </label_select_only>

            <!-- TODO get selected labels from this component
                way to use slots maybe? or just emit event
                 -->
          </div>


          <div v-if="template.kind === 'condition' ">

            <!-- select operator (equals, less than, greater than)  -->
            <v-select :items="operator_list"
                      v-model="condition_operator_select_placeholder"
                      label="Operator"
                      :disabled="loading"
                      item-text="pretty_text"
                      return-object
                      @change="">
            </v-select>

            <!-- select count  -->
            <v-slider min="0"
                      max="100"
                      label="Count"
                      v-model="condition.right_operand"
                      thumb-label="always"
                      >
            </v-slider>

          </div>

          <div v-if="template.kind === 'email' ">


            <!-- email to send to (defaults to user email) -->
            <v-text-field label="Email"
                          append-icon="email"
                          v-model="email.email_send_to"
                          validate-on-blur
                          :rules="[rules.email]">
            </v-text-field>

          </div>

          <div v-if="template.kind === 'webhook' ">


            <!-- email to send to (defaults to user email) -->
            <v-text-field label="URL"
                          append-icon="url"
                          v-model="webhook.url_to_post"
                          validate-on-blur>
            </v-text-field>
            <v-text-field label="Webhook Secret"
                          append-icon="password"
                          v-model="webhook.secret_webhook"
                          validate-on-blur>
            </v-text-field>

          </div>


          <div v-if="template.kind === 'overlay' ">


            <!-- TODO condition on kind being text or
                image and show that / do something -->

            <!-- WIP WIP WIP
            <v-text-field label="Email"
                          append-icon="email"
                          v-model="email.email_send_to"
                          validate-on-blur
                          :rules="[rules.email]">
            </v-text-field>
            -->

             <h2> On detections of </h2>

            <label_select_only
             :project_string_id="project_string_id"
              @label_file="recieve_label_file($event)"
                               >
            </label_select_only>

            <!-- TODO position / size stuff
                assume default for now -->

            <!-- TODO only show this after trigger something
                to get action id -->


            <!-- We have to create the id before upload
                So either show_overlay_upload is false
                and option to do it or true
                success sets it to true
                -->

            <v-btn v-if="show_overlay_upload == false "
                  @click="api_action_update_or_new(mode)"
                 :loading="loading"
                 :disabled="loading"
                 color="primary">
              Next
            </v-btn>

            <div v-if="show_overlay_upload == true">

              <h2> Upload an overlay image </h2>

              <vue-dropzone ref="action_overlay"
                            id="dropzone"
                            :options="dropzoneOptions">
              </vue-dropzone>

            </div>

          </div>


          <!-- Hide on overlay since already created -->

          <v-btn v-if="mode == 'NEW' && template.kind != 'overlay'"
                  @click="api_action_update_or_new('NEW')"
                 :loading="loading"
                 :disabled="loading"
                 color="primary">
            Create
          </v-btn>

           <v-btn v-if="mode == 'UPDATE' "
                  @click="api_action_update_or_new('UPDATE')"
                 :loading="loading"
                 :disabled="loading"
                 color="primary">
            Update
          </v-btn>

          <v_error_multiple :error="error">
          </v_error_multiple>

          <v-alert type="success"
                   :value="success"
                   dismissible
                   >
            Success.
          </v-alert>

        </v-layout>
      </v-container>

    </v-card>

  </div>
</template>

<script lang="ts">


import axios from '../../services/customInstance';
import label_select_only from '../label/label_select_only.vue'


 import Vue from "vue"; export default Vue.extend( {

   name: 'action_new_or_update',

   components: {

     label_select_only : label_select_only

    },

    props: {
      'project_string_id' : {
        default: null
      },
      'flow_id' : {
        default: null
      },
      'mode' : {
        default: 'NEW'
      },
      'action_prop' : {
        default: null
      },
      'last_action' : {
        default: null
      }
    },

    data() {
      return {

        loading: false,
        error: {},
        success: false,

        show_overlay_upload: false,

        // ACTION is a COMPUTED property see below

        // brain_run
        brain_run : {

        },


        // COUNT
         operator_list: [
          {
            'pretty_text': 'Equals ( == )',
            'kind': '=='
          },
          {
            'pretty_text': 'Greater then ( > )',
            'kind': '>'
          },
          {
            'pretty_text': 'Greater or Equal ( >= )',
            'kind': '>='
          },
          {
            'pretty_text': 'Less then ( < )',
            'kind': '<'
          },
          {
            'pretty_text': 'Less then or Equal ( <= )',
            'kind': '<='
          },
          {
            'pretty_text': 'Not equal ( != )',
            'kind': '!='
          }
          ]
        ,

        count: {
          label_file_id: null
        },

        condition: {
          right_operand: 0,
          operator: null
        },

        // workaround becuase the select thing returns an object
        // But we want to send just .kind (string) to backend
        condition_operator_select_placeholder : {
          kind : null
        },

        // EMAIL
        email: {

          send_to: null

        },
        // WEBHOOK
        webhook: {

          url_to_post: null,
          secret_webhook: null,

        },

        rules: {
          email: (value) => {
            const pattern = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
            return pattern.test(value) || 'Invalid e-mail.'
          }
        },


        overlay: {
          kind : "image"
        },

        // TEMPLATES


        template_list: [
          /*
           * // new file is default action for now
          {
            'text': 'New File',
            'kind': 'new_file',
            'icon': ''
          },
          */
          /*
          {
            'text': 'Run a Brain',
            'kind': 'brain_run',
            'icon': 'mdi-brain'
          },
          */
          {
            'text': 'Count a label',
            'kind': 'count',
            'icon': 'mdi-numeric'
          },
          {
            'text': 'Send an Email',
            'kind': 'email',
            'icon': 'email'
          },
          {
            'text': 'POST To Webhook',
            'kind': 'webhook',
            'icon': 'mdi-network'
          },
          {
            'text': 'Condition on',
            'kind': 'condition',
            'icon': 'mdi-function-variant'
          },
          {
            'text': 'Overlay',
            'kind': 'overlay',
            'icon': 'layers'
          }
        ]
        ,

        template : {
          kind : 'count'
        },

        valid_next_actions : {
          // TODO would like to get count/condition up here
		      'init' : ["email", "webhook"],
		      'brain_run' : ["count", "email", "overlay"],
		      'count' : ["condition", "email"],
		      'condition' : ["email", "webhook"]
          //'overlay' : ["email"]
		     },

        action_id: null


      }
    },

    computed: {

      template_list_valid: function() {

        if (!this.valid_action_list) {
          //console.log("valid_action_list is not valid")
          return
        }

        var valid_list = []

        for (let template of this.template_list) {

          if (this.valid_action_list.includes(template.kind) ) {

            valid_list.push(template)

          }
        }

        return valid_list

      },

      // ACTION
      action: function () {

        // Remap as workaround since select returns
        // object...
        let count = this.count

        let condition = this.condition
        condition.operator = this.condition_operator_select_placeholder.kind

        return {
          id: this.action_id,
          overlay: this.overlay,
          kind : this.template.kind,
          brain_run: this.brain_run,
          count: count,
          condition: condition,
          email: this.email,
          webhook: this.webhook,
          flow_id: Number(this.flow_id)
        }
      },

      valid_action_list: function () {
        if (this.last_action) {
          return this.valid_next_actions[this.last_action.kind]
        }
      },

      dropzoneOptions: function () {

        return {
          url: '/api/v1/project/' + this.project_string_id +
            '/action/overlay/image',
          maxFiles: 10,
          parallelUploads: 1,
          thumbnailWidth: 150,
          maxFilesize: 30,
          dictDefaultMessage: "Drop overlay here to upload",
          header: {
            "action_id": this.action.id
          }
        }
      }

    },
    created() {

      if (this.mode == "UPDATE") {
        this.load_existing_action()
      }

    },
    mounted() {

    },
    methods: {

      load_existing_action: function () {

        // TODO review if there's a way we can load this
        // as a dict... declaring individually doesn't feel great

        // This is clearly pretty brittle
        // but with it relying on computed props
        // and the whole messed up front vs back end dict
        // formats I don't see a super clear other way
        // somethin to think about

        // plus whole thing about not using dicts for default values

        this.action_id = this.action_prop.id

        this.template.kind = this.action_prop.kind

        if (this.template.kind == "count") {
           this.count.label_file_id = this.action_prop.count.label_file.id
        }

        if (this.template.kind == "brain_run") {
          this.brain_run = this.action_prop.brain_run
        }

        if (this.template.kind == "condition") {
          this.condition = this.action_prop.condition

          // handle special case
          let operator_kind = this.condition.kind
          this.condition_operator_select_placeholder.kind = operator_kind
        }

        if (this.template.kind == "email") {
          this.email = this.action_prop.email
        }

        if (this.template.kind == "overlay") {
           this.overlay.label_file_id = this.action_prop.overlay.label_file.id
           this.overlay = this.action_prop.overlay
        }


      },

      recieve_label_file: function (label_file) {

        this.count.label_file_id = label_file.id

        this.overlay.label_file_id = label_file.id

      },

      recieve_brain: function (brain) {

        // TODO maybe just to "brain" not "brain_run"

        this.brain_run.id = brain.id

      },

      // Not tested for update, only for new

      api_action_update_or_new: function (mode) {

        this.loading = true
        this.error = {}
        this.success = false

        axios.post(
          '/api/v1/project/' + this.project_string_id +
          '/action/single',
          {
            action: this.action,
            mode: mode

          }).then(response => {

            //this.action = response.data.action

            // TODO clear action stuff??

            this.$store.commit('action_list_refresh')

            this.success = true
            this.loading = false


            // also careful as we require this for both updates
            // and new
            // careful to make use of template.kind before it gets set to null
            if (this.template.kind == "overlay") {
              this.show_overlay_upload = true
            }


            // reset
            if (this.mode == "NEW") {

              // could also reset values for specific actions
              // but could be fiddly
              // may want to move that to a shared default function then
              // can load at init too ro something

              this.template.kind = null
            }




          }).catch(error => {

            if (error.response.status == 400) {
              this.error = error.response.data.log.error
            }
            this.loading = false
            console.log(error)
          });

      }

    }
  }
) </script>
