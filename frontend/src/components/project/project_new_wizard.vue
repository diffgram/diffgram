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
            Invite Team Members
          </v-stepper-step>
          <v-divider></v-divider>
          <v-stepper-step
            editable
            :complete="step > 5"
            step="5">
            Create Task Templates
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
          <v-stepper-content step="3" style="height: 100%">
            <div class="d-flex justify-end">
              <v-btn x-small
                     @click="go_to_step(4)"
                     class="text-right ml-auto"
                     color="secondary">

                <v-icon>mdi-debug-step-over</v-icon>
                Skip, I will upload files later
              </v-btn>
            </div>
            <upload_step_wizard
              @upload_success="on_upload_success"
              :project_string_id="project_string_id">

            </upload_step_wizard>

          </v-stepper-content>
          <v-stepper-content step="4" style="height: 100%">
            <div class="d-flex justify-end">
              <v-btn x-small
                     @click="go_to_step(5)"
                     class="text-right ml-auto"
                     color="secondary">

                <v-icon>mdi-debug-step-over</v-icon>
                Skip, I will invite members later
              </v-btn>
            </div>
            <project_members_step
              @member_invited="on_member_invited"
              :project_string_id="project_string_id">
            </project_members_step>
            <div class="d-flex justify-end">
              <v-btn x-large
                     @click="go_to_step(5)"
                     :disabled="!member_invited"
                     class="text-right ml-auto"
                     color="secondary">
                Continue
              </v-btn>
            </div>
          </v-stepper-content>

          <v-stepper-content step="5" style="height: 100%">
            <div class="d-flex justify-end">
              <v-btn x-small
                     @click="go_to_home"
                     class="text-right ml-auto"
                     color="secondary">

                <v-icon>mdi-debug-step-over</v-icon>
                Skip, I'll create the task template later
              </v-btn>
            </div>
            <welcome_builder

            >
            </welcome_builder>

          </v-stepper-content>

        </v-stepper-items>

      </v-stepper>

    </v-card-text>
  </v-card>
</template>

<script lang="ts">

import axios from 'axios';
import project_new from './project_new';
import project_members_step from './project_members_step';
import labels_attributes_manager from '../label/labels_attributes_manager';
import welcome_builder from '../annotation/welcome_builder';
import upload_step_wizard from '../input/upload_step_wizard';

import Vue from "vue";
export default Vue.extend( {
  name: 'new_project_wizard',
  components:{
    project_new,
    upload_step_wizard,
    project_members_step,
    labels_attributes_manager,
    welcome_builder
  },
  data() {
    return {
      step: 1,
      global_progress: 0,
      project_string_id: null,
      member_invited: false,
    }
  },
  computed: {

  },
  created() {
  },
  methods: {
    on_member_invited: function(){
      this.member_invited = true;
    },
    go_to_home: function(){
      this.$router.push('/')
    },
    on_upload_success: function(){
      this.step = 4;
    },
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
