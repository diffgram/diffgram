<template>

  <v-dialog v-model="is_open" width="1500px" id="task-input-list-dialog" style="min-height: 800px">
    <v-card elevation="0">
      <v-card-text>
        <v-stepper v-model="el">
          <v-stepper-header>
            <v-stepper-step
              :complete="el > 1"
              step="1"
            >
              Start
            </v-stepper-step>

            <v-divider></v-divider>

            <v-stepper-step
              :complete="el > 2"
              step="2"
            >
              Upload Prelabled Data
            </v-stepper-step>

            <v-divider></v-divider>

            <v-stepper-step
              :complete="el > 3"
              step="3">
              Match data to Diffgram Schema
            </v-stepper-step>
            <v-divider></v-divider>
            <v-stepper-step :complete="el > 4" step="4">
              Confirm Upload
            </v-stepper-step>
          </v-stepper-header>
          <v-stepper-items>
            <v-stepper-content step="1">
              <h1 class="pa-10 black--text">Welcome to the file Upload wizard!</h1>
              <v-layout class="d-flex column justify-center">
                <h2 class="ma-8 black--text">Do you want to add prelabeled data to the files you uploaded?</h2>
                <div class="d-flex justify-center align-center">
                  <v-btn x-large class="secondary lighten-2 ma-8" @click="el = 2">Add Prelabeled Data</v-btn>
                  <v-btn x-large class="secondary lighten-1 ma-8" @click="el = 4">Upload Without Data</v-btn>
                </div>
              </v-layout>
            </v-stepper-content>
            <v-stepper-content step="2">
              <h1 class="pa-10 black--text">Step 2</h1>
              <v-btn x-large class="secondary lighten-1 ma-8" @click="el = 3">Continue</v-btn>
            </v-stepper-content>

            <v-stepper-content step="3">
              <h1 class="pa-10 black--text">Step 3</h1>
              <v-btn x-large class="secondary lighten-1 ma-8" @click="el = 4">Continue</v-btn>
            </v-stepper-content>

            <v-stepper-content step="4">
              <h1 class="pa-10 black--text">Confirm the Upload</h1>
              <v-layout class="d-flex column justify-center">
                <h2 class="ma-8 black--text">You are about to upload the {{file_list.length}} file(s):</h2>

                  <v-list-item
                    v-for="(item, i) in file_list"
                    :key="i"
                    dense
                    two-line
                  >
                    <v-list-item-icon>
                      <v-icon v-text="'mdi-file'"></v-icon>
                    </v-list-item-icon>
                    <v-list-item-title>
                      <v-list-item-title v-text="item.name"></v-list-item-title>
                    </v-list-item-title>
                  </v-list-item>
                <v-btn x-large class="success ma-8" @click="el = 4">Upload to Diffgram</v-btn>
              </v-layout>
            </v-stepper-content>

          </v-stepper-items>

        </v-stepper>

      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
  import input_view from './input_view'
  import axios from 'axios';
  import Vue from "vue";

  export default Vue.extend({
      name: 'upload_wizard_dialog',
      components: {
        input_view
      },
      props: {
        'project_string_id': {
          default: null
        },
        'file_list': {
          default: []
        }

      },

      data() {

        return {
          is_open: false,
          el: 1,
        }


      },
      computed: {},
      watch: {},
      mounted() {
      },

      beforeDestroy() {

      },

      methods: {
        async open() {
          this.is_open = true;
        }
      }
    }
  ) </script>

