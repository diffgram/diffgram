<template>
  <v-card elevation="0">
    <v-card-text>
      <v-stepper v-model="step" :non-linear="true" style="height: 100%;" @change="on_change_step">
        <v-stepper-header class="ma-0 pl-8 pr-8">
          <v-stepper-step
            :complete="step > 1"
            step="1"
          >
            Select Connection
          </v-stepper-step>
          <v-divider></v-divider>
          <v-stepper-step
            :complete="step > 2"
            step="2"
            :editable="project_migration_data.connection != undefined"
          >
            Import Configuration
          </v-stepper-step>
          <v-divider></v-divider>
          <v-stepper-step
            :complete="step > 3"
            step="3"
            :editable="project_migration_data.connection != undefined"
                          >
            Start
          </v-stepper-step>
        </v-stepper-header>
        <v-progress-linear
          color="secondary"
          striped
          value="global_progress"
          height="12"
        >
        </v-progress-linear>

        <v-stepper-items style="height: 100%">
          <v-stepper-content step="1" style="height: 100%">

            <project_migrator_connection_step
              @next_step="go_to_step(2)"
              @connection_changed="set_connection"
              :project_string_id="project_string_id">

            </project_migrator_connection_step>

          </v-stepper-content>

          <v-stepper-content step="2" style="height: 100%">
            <project_migrator_config_step :project_migration_data="project_migration_data" :project_string_id="project_string_id">

            </project_migrator_config_step>

          </v-stepper-content>

          <v-stepper-content step="3" style="height: 100%">


          </v-stepper-content>

        </v-stepper-items>

      </v-stepper>

    </v-card-text>
  </v-card>
</template>

<script lang="ts">

import project_migrator_connection_step from './project_migrator_connection_step'
import project_migrator_config_step from './project_migrator_config_step'

import Vue from "vue";
export default Vue.extend( {
  name: 'project_migrator_wizard',
  props:{
    project_string_id:{
      default: null
    }
  },
  components:{
    project_migrator_connection_step,
    project_migrator_config_step,
  },
  data() {
    return {
      step: 1,
      global_progress: 0,
      connection: undefined,
      project_migration_data:{
        connection: undefined,
        labelbox_project_id: null
      }
    }
  },

  computed: {

  },
  created() {

  },
  methods: {
    go_to_step: function(step){
      this.step = step
    },
    go_back_a_step: function(){
      this.step -= 1
    },
    on_change_step: function(){

    },
    set_connection: function(conn){
      this.project_migration_data.connection = conn;
    }
  }
}

) </script>
