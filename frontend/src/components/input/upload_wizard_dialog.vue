<template>

  <v-dialog v-model="is_open" width="1500px" id="task-input-list-dialog" style="min-height: 800px" persistent>
    <v-stepper v-model="el" class="pa-8" non-linear>
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
          Prepare Prelabeled Data
        </v-stepper-step>
        <v-stepper-step
          :complete="el > 4"
          step="4">
          Match data to Diffgram Schema
        </v-stepper-step>
        <v-divider></v-divider>
        <v-stepper-step :complete="el > 5" step="5">
          Confirm Upload
        </v-stepper-step>
      </v-stepper-header>

      <v-stepper-items>
        <v-stepper-content step="1">
          <h1 class="pa-10 black--text">Welcome to the file Upload wizard!</h1>
          <v-layout class="d-flex column justify-center">
            <h2 class="ma-8 black--text">Do you want to add prelabeled data to the files you uploaded?</h2>
            <div class="d-flex justify-center align-center">
              <v-btn x-large class="primary lighten-1 ma-8" @click="el = 2"><v-icon>mdi-file</v-icon> Add Prelabeled Data</v-btn>
              <v-btn x-large class="primary lighten-1 ma-8" @click="el = 5"><v-icon>mdi-upload</v-icon> Upload Without Data</v-btn>
            </div>
          </v-layout>
        </v-stepper-content>


        <v-stepper-content step="2">
          <h1 class="pa-10 black--text">Upload a JSON or CSV file with the labeled data:</h1>
          <ul>
            <li>
              <p>
                This file should contain all the labeled instances matched with the file you want to attach.
              </p>
            </li>
            <li>
              <p>
               Must include a field defining the instance type.
                Possible types are: "box", "polygon", "cuboid", "ellipse", "point", "line".
              </p>
            </li>
            <li>
              <p>If the file is a JSON file it should be an array where each item is an instance.</p>
            </li>
            <li>
              <p>If the file is a CSV file, each row should correspond to a specific instance.</p>
            </li>
          </ul>
          <v-container>
            <vue-dropzone class="mb-12 d-flex align-center justify-center" ref="prelabelDropzone"
                          id="dropzonePreLabels"
                          data-cy="vue-dropzone"
                          style="min-height: 120px"
                          :useCustomSlot=true
                          :options="dropzoneOptions">

            </vue-dropzone>
          </v-container>
          <v-container class="d-flex justify-end">
            <v-btn :disabled="pre_labels_file_list.length !== 1" x-large class="primary lighten-1 ma-8" @click="el = 3">Continue</v-btn>
          </v-container>
        </v-stepper-content>

        <v-stepper-content step="3">
          <h1 class="pa-10 black--text">What Types of Instances Are you Uploading?</h1>
          <v-layout class="d-flex flex-wrap justify-center align-center pa-10">
            <v-checkbox
              v-model="included_instance_types.box"
              label="Box"
              color="secondary"
              :value="true"
              hide-details
            ></v-checkbox>
            <v-checkbox
              v-model="included_instance_types.polygon"
              label="Polygon"
              color="secondary"
              :value="true"
              hide-details
            ></v-checkbox>
            <v-checkbox
              v-model="included_instance_types.line"
              label="Line"
              color="secondary"
              :value="true"
              hide-details
            ></v-checkbox>
            <v-checkbox
              v-model="included_instance_types.point"
              label="Point"
              color="secondary"
              :value="true"
              hide-details
            ></v-checkbox>
            <v-checkbox
              v-model="included_instance_types.cuboid"
              label="Cuboid"
              color="secondary"
              :value="true"
              hide-details
            ></v-checkbox>
            <v-checkbox
              v-model="included_instance_types.ellipse"
              label="Ellipse"
              color="secondary"
              :value="true"
              hide-details
            ></v-checkbox>
          </v-layout>
          <v-layout class="d-flex justify-end">
            <v-btn x-large
                   class="secondary lighten-1 ma-8"
                   :disabled="!at_least_one_instance_type_selected"
                   @click="el = 4">
              Continue
            </v-btn>
          </v-layout>
        </v-stepper-content>

        <v-stepper-content step="4">
          <h1 class="pa-10 black--text">Match Fields to Diffgram Schema</h1>
          <v-expansion-panels accordion>
            <v-expansion-panel key="box" v-if="included_instance_types.box">
              <v-expansion-panel-header>Box Type</v-expansion-panel-header>
              <v-expansion-panel-content>
                <v-layout class="d-flex column">
                  <v-row>
                    <v-col cols="12" class="d-flex">
                      <h4>X MAX:</h4>
                      <v-select :items="pre_label_key_list"></v-select>
                    </v-col>
                  </v-row>
                  <v-row>
                    <v-col cols="12" class="d-flex">
                      <h4>Y MAX:</h4>
                      <v-select :items="pre_label_key_list"></v-select>
                    </v-col>
                  </v-row>
                  <v-row>
                    <v-col cols="12" class="d-flex">
                      <h4>X MIN:</h4>
                      <v-select :items="pre_label_key_list"></v-select>
                    </v-col>
                  </v-row>
                  <v-row>
                    <v-col cols="12" class="d-flex">
                      <h4>Y MIN:</h4>
                      <v-select :items="pre_label_key_list"></v-select>
                    </v-col>
                  </v-row>
                </v-layout>
              </v-expansion-panel-content>
            </v-expansion-panel>
            <v-expansion-panel key="polygon" v-if="included_instance_types.polygon">
              <v-expansion-panel-header>Polygon Type</v-expansion-panel-header>
              <v-expansion-panel-content>

              </v-expansion-panel-content>
            </v-expansion-panel>
            <v-expansion-panel key="point" v-if="included_instance_types.point">
              <v-expansion-panel-header>Point Type</v-expansion-panel-header>
              <v-expansion-panel-content>

              </v-expansion-panel-content>
            </v-expansion-panel>
            <v-expansion-panel key="line" v-if="included_instance_types.line">
              <v-expansion-panel-header>Line Type</v-expansion-panel-header>
              <v-expansion-panel-content>

              </v-expansion-panel-content>
            </v-expansion-panel>
            <v-expansion-panel key="cuboid" v-if="included_instance_types.cuboid">
              <v-expansion-panel-header>Cuboid Type</v-expansion-panel-header>
              <v-expansion-panel-content>

              </v-expansion-panel-content>
            </v-expansion-panel>
            <v-expansion-panel key="ellipse" v-if="included_instance_types.ellipse">
              <v-expansion-panel-header>Ellipse Type</v-expansion-panel-header>
              <v-expansion-panel-content>

              </v-expansion-panel-content>
            </v-expansion-panel>
          </v-expansion-panels>
        </v-stepper-content>

        <v-stepper-content step="5">
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
          diffgram_schema_mapping: {
            box: {
              x_min: null,
              x_max: null,
              y_min: null,
              y_max: null,
            },
            points: {
              points: null,
            },
            cuboid: {
              front_face_x_min: null,
              front_face_x_max: null,
              front_face_y_min: null,
              front_face_y_max: null,
              rear_face_x_min: null,
              rear_face_x_max: null,
              rear_face_y_min: null,
              rear_face_y_max: null,
            },
            ellipse: {
              points: null,
            },
            line: {
              points: null,
            },
          },
          included_instance_types:{
            box: false,
            polygon: false,
            cuboid: false,
            ellipse: false,
            point: false,
            line: false,
          },
          is_open: false,
          el: 1,
          preLabels: null,
          pre_labels_file_list: [],
          pre_label_key_list: [],
        }


      },
      computed: {
        at_least_one_instance_type_selected: function(){
          for(const key in this.included_instance_types){
            if (this.included_instance_types[key]){
              return true
            }
          }
          return false
        },
        dropzoneOptions: function () {

          // CAUTION despite being a computed property any values that CHANGE
          // after component is created don't seem to get actually reflected sometimes...
          // The drop zone options things doesn't update well from vuex, depsite being a computed prop
          // I think the actual vue js dropzone thing may be updating properly though
          // (Context of moving to using drop_zone_sending_event() for thing from vuex)
          const $vm = this;
          return {
            init: function () {
              this.on("addedfile", async function (file) {
                const textData = await file.text();
                if(file.type === 'application/json'){
                  this.preLabels = JSON.parse(textData);
                  const pre_label_keys = $vm.extract_pre_label_key_list(this.preLabels);
                  $vm.pre_label_key_list = [...pre_label_keys];
                  this.emit('complete', file);
                  this.emit('success', file);
                  $vm.pre_labels_file_list.push(file);
                }
                else if(file.type === 'text/csv'){

                }
              });

            },
            url: '/api/walrus/project/' + this.project_string_id + '/upload/large',
            chunking: true,
            maxFiles: 1,
            autoProcessQueue: false,
            height: 120,
            thumbnailWidth: 80,
            thumbnailHeight: 80,
            maxFilesize: 5000,
            acceptedFiles: ".csv, .json"
          }

        },
      },
      watch: {},
      mounted() {
      },

      beforeDestroy() {

      },

      methods: {
        extract_pre_label_key_list: function(preLabelsObject){
          const result = []
          for(const elm of preLabelsObject){
            for(const key in elm){
              if(!result.includes(key)){
                result.push(key)
              }
            }
          }
          return result;
        },
        async open() {
          this.is_open = true;
        }
      }
    }
  ) </script>

