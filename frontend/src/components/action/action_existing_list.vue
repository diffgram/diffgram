<template>
<div id="">

<v-card>
  <v-container>

      <v-layout>

          <v-layout>

            <action_new_or_update
                :project_string_id="project_string_id"
                :flow_id = "flow_id"
                :last_action = "last_action"
                    >
            </action_new_or_update>

              <!-- Would like to use parent action to action_new -->
              <!-- 
                :parent_action_id = "parent_action_id" -->

          </v-layout>


      <v-layout column>

        <v_error_multiple :error="error">
        </v_error_multiple>


          <v-container fluid grid-list-md>

            <draggable
                v-model="action_list"
                draggable=false
                        >

              <template v-for="item in action_list">


                  <action_existing_single
                      :project_string_id="project_string_id"
                      :action="item"
                      >
                  </action_existing_single>

              </template>

            </draggable>


          </v-container>


      </v-layout>

    </v-layout>
  </v-container>

</v-card>

</div>
</template>

<script lang="ts">


import axios from 'axios';
import draggable from 'vuedraggable'

import action_new_or_update from './action_new_or_update.vue';
import action_existing_single from './action_existing_single.vue'


 import Vue from "vue"; export default Vue.extend( {

   // TODO may want to rename now that seeing
   // dependency between knowing which parent / "were" we are creaing a new
   // action and parent.

    name: 'action_existing_list',

    components: {  
      action_new_or_update : action_new_or_update,
      action_existing_single: action_existing_single,
      draggable: draggable
    },

    props: {

      'project_string_id' : {
        default: null
      },
      'flow_id' : {
        default: null
      }

    },

    data() {
      return {

        loading: false,
        error: {},
        success: false,

        name: null,

        action_list: [],

        last_action: {
          kind: "init"
        }

      }
    },

    watch: {

      // for "updates in place" to page.
      flow_id() {
        this.api_action_list()
      }

    },

    created() {

       this.api_action_list()

    },
    mounted() {

      // ie triggered by  this.$store.commit('action_list_refresh')
      // defined in store.js action 
      var self = this
      this.refresh_watcher = this.$store.watch((state) => {
        return this.$store.state.action.refresh_list
      },
        (new_val, old_val) => {     
          self.api_action_list()      
        },
      )
    },
    destroyed() {
      this.refresh_watcher() // destroy
    },
    computed: {
    },
    methods: {
      
      api_action_list: function () {

        this.loading = true
        this.error = {}
        this.success = false

        axios.post(
          '/api/v1/project/' + this.project_string_id +
          '/action/list',
          {
            flow_id: Number(this.flow_id)

          }).then(response => {

            this.action_list = response.data.action_list

            if (this.action_list.length != 0) {
              this.last_action = this.action_list.slice(-1)[0]
            }

            this.success = true
            this.loading = false

          }).catch(error => {

            if (error.response.status == 400) {
              this.error = error.response.data.log.error
            }
            this.loading = false
            console.log(error)
          });

      },


    }
  }
) </script>
