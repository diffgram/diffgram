<template>
  <div id="">


    <v-card>
      <v-container>

        <v-layout column>

          <!-- TODO prefer to get from tempalte? -->
          <!-- {{ action.template.public_name }} -->


          <!-- BRAIN -->
         <div v-if="action.kind === 'brain_run' ">

           <h3>
              <v-icon>mdi-brain</v-icon>
              Run a Brain
           </h3>

           Brain name: {{ action.brain_run.name }}

          </div>


          <!-- COUNT -->
          <div v-if="action.kind === 'count' ">


            <h3>
              <v-icon>mdi-numeric</v-icon>
              Count a label
            </h3>

            <div v-if="action.count.label_file">
                 <h2> {{ action.count.label_file.label.name }} </h2>
            </div>

          </div>


           <!-- CONDITION -->
          <div v-if="action.kind === 'condition' ">

            <h3>
              <v-icon>mdi-function-variant</v-icon>
              Condition on
            </h3>

            <h2> {{ action.condition.operator }}
               {{ action.condition.right_operand }}
            </h2>

          </div>


          <!-- EMAIL -->
          <div v-if="action.kind === 'email' ">

            <h3>
              <v-icon>email</v-icon>
              Send an email
            </h3>

            <h2>
            To: {{ action.email.send_to }}
            </h2>

          </div>

          <!-- WEBHOOK -->
          <div v-if="action.kind === 'webhook' ">

            <h3 class="mb-4">
              <v-icon>webhook</v-icon>
              POST TO URL
            </h3>
            <p class="mb-0"><strong> Url:</strong></p>
            <p>
              {{ action.webhook.url_to_post }}
            </p>

          </div>

         <!-- Overlay -->
        <div v-if="action.kind === 'overlay' ">

          <h3>
            <v-icon>layers</v-icon>
            Overlay
          </h3>

          <!--
          <h2> {{ action_event.overlay }}

          </h2>
           -->

          <!-- for some strange reason this is hidden
              in an array-->
          <div v-if="action.overlay.overlay_image">
            <img v-if="action.overlay.overlay_image[0]"
                 :src="action.overlay.overlay_image[0].url_signed">
          </div>

          <div v-if="action.overlay.label_file">
                <h2> On
             {{ action.overlay.label_file.label.name }}
              Detections
             </h2>
          </div>


        </div>



          <v_error_multiple :error="error">
          </v_error_multiple>

          <!-- Dec 26, 2019
            removed "show more / 3 dots" menu till we have more stuff
            if add back in use new button_with_menu thing -->

          <div class="text-right">

            <button_with_menu
                tooltip_message="Edit"
                icon="edit"
                :loading="loading"
                :disabled="loading"
                color="primary"
                :close_by_button="true"
                    >
              <template slot="content">

                <action_new_or_update
                    :project_string_id="project_string_id"
                    :flow_id = "action.flow_id"
                    :action_prop = "action"
                    :mode = " 'UPDATE' "
                        >
                </action_new_or_update>

              </template>
            </button_with_menu>

            <button_with_confirm
              @confirm_click="api_action_archive('ARCHIVE')"
              color="red"
              icon="archive"
              :icon_style="true"
              tooltip_message="Archive"
              confirm_message="Archive"
              :loading="loading">
            </button_with_confirm>

          </div>
        </v-layout>
      </v-container>

    </v-card>


  </div>
</template>

<script lang="ts">


import axios from 'axios';
import action_new_or_update from './action_new_or_update.vue';


 import Vue from "vue"; export default Vue.extend( {
    name: 'action_existing_single',
    components: {
        action_new_or_update: action_new_or_update
    },
    props: {

      'project_string_id' : {
        default: null
      },

      // TODO this expects an action element, ie populated from flow page?
      'action' : {
        default: {
          kind : null,
          brain: {},
          label: {},
          template: {}
        }
      }
    },

    data() {
      return {

        loading: false,
        error: {},
        success: false,

        name: null,

        action_menu: false,
        show_menu: false,



      }
    },
    created() {

    },
    computed: {

    },
    methods: {


      // this is for ARCHIVE only
      // Since UPDATE is done within action_new_or_update
      // The API itself is shared, so still need to pass mode

      api_action_archive: function (mode) {

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


            this.$store.commit('action_list_refresh')

            this.success = true
            this.loading = false



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
