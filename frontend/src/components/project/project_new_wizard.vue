<template>
  <v-card elevation="0">
    <v-card-text>
      <v-stepper v-model="step" :non-linear="true" style="height: 100%;" @change="on_change_step">
        <v-stepper-header class="ma-0 pl-8 pr-8">
          <v-stepper-step
            editable
            :complete="step > 1"
            step="1"
          >
            Create Project
          </v-stepper-step>
          <v-divider></v-divider>
          <v-stepper-step
            editable
            :complete="step > 2"
            step="2"
          >
            Create Labels & Attributes
          </v-stepper-step>
          <v-divider></v-divider>
          <v-stepper-step
            editable
            :complete="step > 3"
            step="3">
            Upload Data
          </v-stepper-step>
          <v-divider></v-divider>
          <v-stepper-step
            editable
            :complete="step > 4"
            step="4">
            Create Task Templates
          </v-stepper-step>
          <v-divider></v-divider>
          <v-stepper-step
            editable
            :complete="step > 5"
            step="4">
            Invite Team Members
          </v-stepper-step>
        </v-stepper-header>
        <v-progress-linear
          color="secondary"
          striped
          v-model="global_progress"
          height="12"
        >
        </v-progress-linear>
        <v-stepper-items style="height: 100%">
          <v-stepper-content step="1" style="height: 100%">
            <project_new
              @project_created="on_project_created"
            ></project_new>
          </v-stepper-content>
          <v-stepper-content step="2" style="height: 100%">
            <labels_attributes_manager
              @skip="go_to_step"
              :project_string_id="project_string_id">

            </labels_attributes_manager>
          </v-stepper-content>
        </v-stepper-items>
      </v-stepper>

    </v-card-text>
  </v-card>
</template>

<script lang="ts">

import axios from 'axios';
import project_new from './project_new';
import labels_attributes_manager from '../label/labels_attributes_manager';

import Vue from "vue";
export default Vue.extend( {
  name: 'new_project_wizard',
  components:{
    project_new,
    labels_attributes_manager
  },
  data() {
    return {
      step: 1,
      global_progress: 0,
      project_string_id: null,
    }
  },
  computed: {

  },
  created() {
  },
  methods: {
    on_project_created: function(project){
      this.project_string_id = project.project_string_id;
      this.step = 2;
    },
    go_to_step: function(step){
      this.step = step
    },
    on_change_step: function(){

    }

  }
}

) </script>
