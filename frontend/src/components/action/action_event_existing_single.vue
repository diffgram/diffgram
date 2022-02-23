<template>
<div id="">
  <v-card>
    <v-container>
    
      <v-layout column>

        <!-- TODO prefer to get from tempalte? --> 
        <!-- {{ action_event.template.public_name }} -->


        <!-- BRAIN -->
        <div v-if="action_event.kind == 'brain_run' ">

          <h3>
            <v-icon>mdi-brain</v-icon>
            Run a Brain
          </h3>

          Status: {{ action_event.brain_run.status }}    

        </div>


        <!-- COUNT -->
        <div v-if="action_event.kind == 'count' ">


          <h3>
            <v-icon>mdi-numeric</v-icon>
            Count a label
          </h3>

          <h2> {{ action_event.count.count }} </h2>

        </div>


          <!-- CONDITION -->
        <div v-if="action_event.kind == 'condition' ">

          <h3>
            <v-icon>mdi-function-variant</v-icon>
            Condition result
          </h3>

          <h2> {{ action_event.condition.condition_result }}
          </h2>

        </div>


        <!-- EMAIL -->
        <div v-if="action_event.kind == 'email' ">

          <h3>
            <v-icon>email</v-icon>
            Send an email
          </h3>

          <h2>
          To: {{ action_event.email.send_to }}
          </h2>
            
        </div>
     
        <!-- Overlay -->
        <div v-if="action_event.kind == 'overlay' ">

          <h3>
            <v-icon>layers</v-icon>
            Overlay result
          </h3>

          <!--
          <h2> {{ action_event.overlay }}

          </h2>
           -->

          <img :src="action_event.overlay.image_rendered.url_signed"
               width="100%"
               >
            

        </div>


        <v_error_multiple :error="error">
        </v_error_multiple>

        <!-- MORE menu
            offset-y
            --> 
        <button_with_menu         
              tooltip_message="More"
              icon="mdi-dots-horizontal"
              color="primary"
              v-if="show_menu"
              class="text-right"
                  >

          <template slot="content">

            <v-card>
              <v-layout column>

                <tooltip_button
                    @click="api_action_event_update('ARCHIVE')"
                    icon="mdi-package-down"
                    :loading="loading"
                    :disabled="loading"
                    tooltip_message="Archive"
                    color="primary">
                </tooltip_button>

              </v-layout>
            </v-card>

          </template>

          </button_with_menu>

      </v-layout>
    </v-container>

  </v-card>

</div>
</template>

<script lang="ts">

 import Vue from "vue"; export default Vue.extend( {
    name: 'action_event_existing_single',
    components: {
    },
    props: {

      'project_string_id' : {
        default: null
      },

      'action_event' : {
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

        show_menu: false


      }
    },
    created() {

    },
    computed: {

    },
    methods: {

    }
  }
) </script>
