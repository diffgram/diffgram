<template>
  <v-card elevation="0">
    <v-card-text>
      <v-stepper v-model="step" :non-linear="true" style="height: 100%;" @change="on_change_step">
        <v-stepper-header class="ma-0 pl-8 pr-8">
          <v-stepper-step
            :complete="step > 1"
            step="1"
          >
            Name
          </v-stepper-step>
          <v-divider></v-divider>
          <v-stepper-step
            :complete="step > 2"
            step="2"                          
            :editable="project_string_id != undefined"
          >
            Label Schema
          </v-stepper-step>
          <v-divider></v-divider>
          <v-stepper-step
            :complete="step > 3"
            step="3"
            :editable="project_string_id != undefined"
                          >
            Upload
          </v-stepper-step>
          <v-divider></v-divider>
          <v-stepper-step
            :complete="step > 4"
            step="4"
            :editable="project_string_id != undefined"
                          >
            Invite Team
          </v-stepper-step>
          <v-divider></v-divider>
          <v-stepper-step
            :complete="step > 5"
            step="5"
            :editable="project_string_id != undefined"
                          >
            Tasks
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
            <project_new
              @project_created="on_project_created"
            ></project_new>
          </v-stepper-content>

          <v-stepper-content step="2" style="height: 100%">

            <labels_attributes_manager
              @skip="go_to_step"
              @back="go_back_a_step()"
              :project_string_id="project_string_id">

            </labels_attributes_manager>
          </v-stepper-content>

          <v-stepper-content step="3" style="height: 100%">

            <upload_step_wizard
              @upload_success="on_upload_success"
              :project_string_id="project_string_id">

            </upload_step_wizard>

            <wizard_navigation
              @next="go_to_step(4)"
              @skip="go_to_step(4)"
              @back="go_back_a_step()">
            </wizard_navigation>

          </v-stepper-content>
          <v-stepper-content step="4" style="height: 100%">

            <project_members_step
              @member_invited="on_member_invited"
              :project_string_id="project_string_id">
            </project_members_step>

            <wizard_navigation
              @next="go_to_step(5)"
              @skip="go_to_step(5)"
              @back="go_back_a_step()">
            </wizard_navigation>

          </v-stepper-content>

          <v-stepper-content step="5" style="height: 100%">

            
            <h1 class="font-weight-medium text--primary">Create Tasks</h1>
            

            <p class="pt-3 text--primary">
              All of your work is saved.
              The next step is to create tasks for human workflow.
              The task creation process will re-use all of the work done so far.
              As you progress through using Diffgram you will likely have many sets of tasks.
              These will all re-use the same project resources, and you will only need to revisit
              this project creation process if you have a majorly different project.
            </p>

            <wizard_navigation
              @skip="go_to_home()"
              @back="go_back_a_step()"
              :next_visible="false">

              <template slot="next">

                <v-btn
                  x-large
                  @click="$router.push('/project/' + $store.state.project.current.project_string_id + '/job/new')"
                  color="success"
                  data-cy="wizard_navigation_next"
                       >
                  Create Tasks
                </v-btn>
     
              </template>
            </wizard_navigation>

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
      project_string_id: undefined,
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
      this.go_to_step(2);
    },
    go_to_step: function(step){
      this.step = step
    },
    go_back_a_step: function(){
      this.step -= 1
    },
    on_change_step: function(){

    }

  }
}

) </script>
