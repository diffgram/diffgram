<template>

  <v-dialog v-if="is_open" v-model="is_open" width="1700px" id="task-input-list-dialog" style="min-height: 800px;" persistent>
    <v-layout style="position: relative; z-index: 999999">
      <v-btn @click="close" icon x-large style="position: absolute; top: 0; right: 0">
        <v-icon>mdi-close</v-icon>
      </v-btn>
    </v-layout>

    <v-stepper v-model="el" class="pa-8" :non-linear="true">

      <v-stepper-header>
        <v-stepper-step
          editable
          :complete="el > 1"
          step="1"
        >
          Start
        </v-stepper-step>
        <v-divider></v-divider>
        <v-stepper-step
          editable
          :complete="el > 2"
          step="2">
          Prepare Prelabeled Data
        </v-stepper-step>
        <v-divider></v-divider>
        <v-stepper-step
          editable
          :complete="el > 3"
          step="3">
          Match data to Diffgram Schema
        </v-stepper-step>
        <v-divider></v-divider>
        <v-stepper-step :complete="el > 4" step="4" editable>
          Confirm Upload
        </v-stepper-step>
      </v-stepper-header>

      <v-stepper-items>
        <v-stepper-content step="1">
          <new_or_update_upload_screen
            @file_list_updated="file_list_updated"
            @change_step_no_annotations="el = 4"
            @change_step_annotations="load_annotations_file"
            ref="new_or_update_upload_screen"
            :project_string_id="project_string_id">

          </new_or_update_upload_screen>
        </v-stepper-content>

        <v-stepper-content step="2">
          <v-layout class="d-flex flex-column justify-center align-center pa-10">

            <v_error_multiple :error="errors_file_schema">
            </v_error_multiple>
            <v-container class="d-flex flex-column pa-0">
              <div class="d-flex justify-start align-center">
                <div class="d-flex flex-column justify-start">
                  <h3 class="pa-2 black--text">* Select the Field Corresponding to the instance type</h3>
                  <p style="font-size: 12px" class="primary--text text--lighten-3"><strong>** Allowed values here are:
                    {{allowed_instance_types}}</strong></p>

                </div>
                <div class="d-flex justify-end flex-grow-1">
                  <v-select class="pt-4"
                            style="max-width: 200px"
                            dense
                            :items="pre_label_key_list"
                            v-model="diffgram_schema_mapping.instance_type">

                  </v-select>
                </div>
              </div>
              <div class="d-flex justify-start align-center">
                <div class="d-flex flex-column justify-start">
                  <h3 class="pa-2 black--text">* Select the Field Corresponding to the File Name</h3>
                  <p style="font-size: 12px" class="primary--text text--lighten-3"><strong>** The value of this key must
                    match with the file name in order to identify the instances.</strong></p>

                </div>
                <div class="d-flex justify-end flex-grow-1">
                  <v-select class="pt-4"
                            style="max-width: 200px"
                            dense
                            :items="pre_label_key_list"
                            v-model="diffgram_schema_mapping.file_name">

                  </v-select>
                </div>
              </div>
              <div class="d-flex justify-start align-center">
                <div class="d-flex flex-column justify-start">
                  <h3 class="pa-2 black--text">** Select the Field Corresponding to the frame number (Video Only)</h3>
                  <p style="font-size: 12px" class="primary--text text--lighten-3"><strong>** For Video Only</strong>
                  </p>

                </div>
                <div class="d-flex justify-end flex-grow-1">
                  <v-select class="pt-4"
                            style="max-width: 200px"
                            dense
                            :items="pre_label_key_list"
                            v-model="diffgram_schema_mapping.frame_number">

                  </v-select>
                </div>
              </div>
              <div class="d-flex justify-start align-center">
                <div class="d-flex flex-column justify-start">
                  <h3 class="pa-2 black--text">Select the Field Corresponding to the Model ID (Optional)</h3>
                  <p style="font-size: 12px" class="primary--text text--lighten-3"><strong>** If model already exists,
                    instances will be binded to existing model.</strong></p>

                </div>
                <div class="d-flex justify-end flex-grow-1">
                  <v-select class="pt-4"
                            style="max-width: 200px"
                            dense
                            :items="pre_label_key_list"
                            v-model="diffgram_schema_mapping.model_id">

                  </v-select>
                </div>
              </div>

              <div class="d-flex justify-start align-center">
                <div class="d-flex flex-column justify-start">
                  <h3 class="pa-2 black--text">Select the Field Corresponding to the Model Run ID (Optional)</h3>
                  <p style="font-size: 12px" class="primary--text text--lighten-3"><strong>** If the run already exists,
                    instances will be binded to existing run.</strong></p>

                </div>
                <div class="d-flex justify-end flex-grow-1">
                  <v-select class="pt-4"
                            style="max-width: 200px"
                            dense
                            :items="pre_label_key_list"
                            v-model="diffgram_schema_mapping.point.model_run_id">

                  </v-select>
                </div>
              </div>

            </v-container>
          </v-layout>
          <v-layout class="d-flex justify-end">
            <v-btn x-large
                   class="secondary lighten-1 ma-8"
                   :disabled="!instance_type_schema_is_set || !file_name_schema_is_set"
                   @click="check_errors_and_go_to_step(3)">
              Continue
            </v-btn>
          </v-layout>
        </v-stepper-content>

        <v-stepper-content step="3">
          <h1 class="pa-10 black--text">Match Fields to Diffgram Schema</h1>
          <v-expansion-panels accordion>
            <v-expansion-panel key="box" class="ma-4" v-if="included_instance_types.box">
              <v-expansion-panel-header color="primary lighten-2" class="text--white">
                <span class="white--text"><strong>Box Type (Click to match schema)</strong></span>
              </v-expansion-panel-header>
              <v-expansion-panel-content>
                <v-layout class="d-flex column">
                  <v-data-table :headers="schema_match_headers" dense :hide-default-footer="true">
                    <template v-slot:body="{ items }">
                      <tbody>
                      <tr v-for="key in Object.keys(diffgram_schema_mapping.box)">
                        <td><strong>{{key}}:</strong></td>
                        <td>
                          Preview Data Here
                        </td>
                        <td class="d-flex align-center">
                          <v-select class="pt-4"
                                    style="max-width: 200px"
                                    dense
                                    @change="check_box_key_structure(key)"
                                    :items="pre_label_key_list"
                                    v-model="diffgram_schema_mapping.box[key]">

                          </v-select>
                        </td>
                        <td>
                          <p style="font-size: 12px" class="primary--text text--lighten-3">
                            <strong>
                              ** {{key}} coordinate must be a number
                            </strong>
                            <strong v-if="valid_points_values_box_instance_type[key]">
                              <v-icon color="success">mdi-check</v-icon>
                              Valid Values
                            </strong>
                            <v_error_multiple dense :error="error_box_instance[key]">
                            </v_error_multiple>
                          </p>

                        </td>
                      </tr>
                      </tbody>
                    </template>
                  </v-data-table>
                </v-layout>
              </v-expansion-panel-content>
            </v-expansion-panel>

            <v-expansion-panel key="polygon" class="ma-4" v-if="included_instance_types.polygon">
              <v-expansion-panel-header color="primary lighten-2" class="text--white">
                <span class="white--text"><strong>Polygon Type (Click to match schema)</strong></span>
              </v-expansion-panel-header>
              <v-expansion-panel-content>
                <v-data-table :headers="schema_match_headers" dense :hide-default-footer="true">
                  <template v-slot:body="{ items }">
                    <tbody>

                    <tr v-if="pre_labels_file_type === 'json'">
                      <td><strong>points:</strong></td>
                      <td>
                        Preview Data Here
                      </td>
                      <td class="d-flex align-center">
                        <v-select class="pt-4"
                                  style="max-width: 200px"
                                  dense
                                  :items="pre_label_key_list"
                                  @change="check_polygon_points_key_structure"
                                  v-model="diffgram_schema_mapping.polygon.points">

                        </v-select>
                      </td>
                      <td>Preview Data</td>
                      <td v-if="pre_labels_file_type === 'json'">
                        <p style="font-size: 12px" class="primary--text text--lighten-3">
                          <strong>
                            ** Points Must be an array of objects with the structure:
                            "{x: Number, y: Number}"
                          </strong>
                          <strong v-if="valid_points_values_polygon">
                            <v-icon color="success">mdi-check</v-icon>
                            Valid Values
                          </strong>
                          <v_error_multiple dense :error="error_polygon_instance">
                          </v_error_multiple>
                        </p>
                      </td>
                      <td v-if="pre_labels_file_type === 'csv'">
                        <p style="font-size: 12px" class="primary--text text--lighten-3">
                          <strong>
                            ** Points must be in 2 columns, one for the X values and one for the Y
                            values. Each column should be comma separated numbers of the corresponding
                            point coordinates.
                          </strong>
                        </p>
                      </td>
                    </tr>
                    </tbody>
                  </template>
                </v-data-table>
              </v-expansion-panel-content>
            </v-expansion-panel>

            <v-expansion-panel key="point" class="ma-4" v-if="included_instance_types.point">
              <v-expansion-panel-header color="primary lighten-2" class="text--white">
                <span class="white--text"><strong>Point Type (Click to match schema)</strong></span>
              </v-expansion-panel-header>
              <v-expansion-panel-content>
                <v-data-table :headers="schema_match_headers" dense :hide-default-footer="true">
                  <template v-slot:body="{ items }">
                    <tbody>
                    <tr v-for="key in Object.keys(diffgram_schema_mapping.point)">
                      <td><strong>point {{key}} value:</strong></td>
                      <td>
                        Preview Data Here
                      </td>
                      <td>
                        <v-select class="pt-4"
                                  style="max-width: 200px"
                                  dense
                                  :items="pre_label_key_list"
                                  @change="check_points_key_structure(key)"
                                  v-model="diffgram_schema_mapping.point[key]">

                        </v-select>
                      </td>
                      <td>
                        <p style="font-size: 12px" class="primary--text text--lighten-3">
                          <strong>
                            ** {{key}} coordinate must be a number
                          </strong>
                          <strong v-if="valid_points_values_point_instance_type[key]">
                            <v-icon color="success">mdi-check</v-icon>
                            Valid Values
                          </strong>
                          <v_error_multiple dense :error="error_point_instance[key]">
                          </v_error_multiple>
                        </p>

                      </td>
                    </tr>
                    </tbody>
                  </template>
                </v-data-table>
              </v-expansion-panel-content>
            </v-expansion-panel>

            <v-expansion-panel key="line" class="ma-4" v-if="included_instance_types.line">
              <v-expansion-panel-header color="primary lighten-2" class="text--white">
                <span class="white--text"><strong>Line Type (Click to match schema)</strong></span>
              </v-expansion-panel-header>
              <v-expansion-panel-content>
                <v-data-table :headers="schema_match_headers" dense :hide-default-footer="true">
                  <template v-slot:body="{ items }">
                    <tbody>
                    <tr v-for="key in Object.keys(diffgram_schema_mapping.line)">
                      <td><strong>line {{key}} value:</strong></td>
                      <td>
                        Preview Data Here
                      </td>
                      <td class="d-flex align-center">
                        <v-select class="pt-4"
                                  style="max-width: 200px"
                                  dense
                                  @change="check_line_key_structure(key)"
                                  :items="pre_label_key_list"
                                  v-model="diffgram_schema_mapping.line[key]">

                        </v-select>
                      </td>
                      <td>
                        <p style="font-size: 12px" class="primary--text text--lighten-3">
                          <strong>
                            ** coordinate must be a number
                          </strong>
                          <strong v-if="valid_points_values_line_instance_type[key]">
                            <v-icon color="success">mdi-check</v-icon>
                            Valid Values
                          </strong>
                          <v_error_multiple dense :error="error_line_instance[key]">
                          </v_error_multiple>
                        </p>


                      </td>
                    </tr>
                    </tbody>
                  </template>
                </v-data-table>
              </v-expansion-panel-content>
            </v-expansion-panel>


            <v-expansion-panel key="cuboid" class="ma-4" v-if="included_instance_types.cuboid">
              <v-expansion-panel-header color="primary lighten-2" class="text--white">
                <span class="white--text"><strong>Cuboid Type (Click to match schema)</strong></span>
              </v-expansion-panel-header>
              <v-expansion-panel-content>
                <v-data-table :headers="schema_match_headers" dense :hide-default-footer="true">
                  <template v-slot:body="{ items }">
                    <tbody>
                    <tr v-for="key in Object.keys(diffgram_schema_mapping.cuboid)">
                      <td><strong>{{key}}:</strong></td>
                      <td>
                        Preview Data Here
                      </td>
                      <td class="d-flex align-center">
                        <v-select class="pt-4"
                                  style="max-width: 200px"
                                  dense
                                  @change="check_cuboid_key_structure(key)"
                                  :items="pre_label_key_list"
                                  v-model="diffgram_schema_mapping.cuboid[key]">
                        </v-select>
                      </td>
                      <td>
                        <p style="font-size: 12px" class="primary--text text--lighten-3">
                          <strong>
                            ** coordinate must be a number
                          </strong>
                          <strong v-if="valid_points_values_cuboid_instance_type[key]">
                            <v-icon color="success">mdi-check</v-icon>
                            Valid Values
                          </strong>
                          <v_error_multiple dense :error="error_cuboid_instance[key]">
                          </v_error_multiple>
                        </p>
                      </td>
                    </tr>


                    </tbody>
                  </template>
                </v-data-table>
              </v-expansion-panel-content>
            </v-expansion-panel>
            <v-expansion-panel key="ellipse" class="ma-4" v-if="included_instance_types.ellipse">
              <v-expansion-panel-header color="primary lighten-2" class="text--white">
                <span class="white--text"><strong>Ellipse Type (Click to match schema)</strong></span>
              </v-expansion-panel-header>
              <v-expansion-panel-content>
                <v-data-table :headers="schema_match_headers" dense :hide-default-footer="true">
                  <template v-slot:body="{ items }">
                    <tbody>
                    <tr v-for="key in Object.keys(diffgram_schema_mapping.ellipse)">
                      <td><strong>{{key}}:</strong></td>
                      <td>
                        Preview Data Here
                      </td>
                      <td class="d-flex align-center">
                        <v-select class="pt-4"
                                  style="max-width: 200px"
                                  dense
                                  @change="check_ellipse_key_structure(key)"
                                  :items="pre_label_key_list"
                                  v-model="diffgram_schema_mapping.ellipse[key]">

                        </v-select>
                      </td>
                      <td>
                        <p style="font-size: 12px" class="primary--text text--lighten-3">
                          <strong>
                            ** value must be a number
                          </strong>
                          <strong v-if="valid_points_values_ellipse_instance_type[key]">
                            <v-icon color="success">mdi-check</v-icon>
                            Valid Values
                          </strong>
                          <v_error_multiple dense :error="error_ellipse_instance[key]">
                          </v_error_multiple>
                        </p>
                      </td>
                    </tr>
                    </tbody>
                  </template>
                </v-data-table>
              </v-expansion-panel-content>
            </v-expansion-panel>
          </v-expansion-panels>
          <div class="d-flex justify-end">
            <v_error_multiple dense :error="errors_instance_schema">
            </v_error_multiple>
            <v-btn @click="check_errors_and_go_to_step(4)" color="primary" x-large> Continue</v-btn>
          </div>
        </v-stepper-content>

        <v-stepper-content step="4">
          <upload_summary
            v-if="file_list_to_upload && pre_labeled_data && diffgram_schema_mapping"
            :file_list="file_list_to_upload.filter(f => f.data_type === 'Raw Media')"
            :project_string_id="project_string_id"
            :pre_labeled_data="pre_labeled_data"
            :diffgram_schema_mapping="diffgram_schema_mapping"
            @upload_raw_media="upload_raw_media"
          ></upload_summary>
        </v-stepper-content>

      </v-stepper-items>

    </v-stepper>
  </v-dialog>
</template>

<script lang="ts">
  import input_view from './input_view'
  import new_or_update_upload_screen from './new_or_update_upload_screen'
  import upload_summary from './upload_summary'
  import axios from 'axios';
  import Vue from "vue";

  export default Vue.extend({
      name: 'upload_wizard_dialog',
      components: {
        input_view,
        upload_summary,
        new_or_update_upload_screen
      },
      props: {
        'project_string_id': {
          default: null
        },

      },

      data() {

        return {
          schema_match_headers: [
            {
              text: 'Diffgram Value',
              align: 'start',
              sortable: false,
              value: 'diffgram_value',
            },
            {
              text: 'Preview Data',
              value: 'preview',
              align: 'start',
              sortable: false,
            },
            {
              text: 'File Value',
              value: 'file_value',
              align: 'start',
              sortable: false,
            },
            {
              text: 'Notes',
              value: 'file_value',
              align: 'start',
              sortable: false,
            },
          ],
          allowed_instance_types: [
            'box',
            'polygon',
            'line',
            'point',
            'cuboid',
            'ellipse',
          ],
          diffgram_schema_mapping: {
            instance_type: null,
            file_name: null,
            frame_number: null,
            model_id: null,
            model_run_id: null,
            box: {
              x_min: null,
              x_max: null,
              y_min: null,
              y_max: null,
            },
            point: {
              x: null,
              y: null,
            },
            polygon: {
              points: null,
            },
            cuboid: {
              front_face_top_left_x: null,
              front_face_top_left_y: null,
              front_face_top_right_x: null,
              front_face_top_right_y: null,
              front_face_bottom_left_x: null,
              front_face_bottom_left_y: null,
              front_face_bottom_right_x: null,
              front_face_bottom_right_y: null,

              rear_face_top_left_x: null,
              rear_face_top_left_y: null,
              rear_face_top_right_x: null,
              rear_face_top_right_y: null,
              rear_face_bottom_left_x: null,
              rear_face_bottom_left_y: null,
              rear_face_bottom_right_x: null,
              rear_face_bottom_right_y: null,

            },
            ellipse: {
              center_x: null,
              center_y: null,
              width: null,
              height: null,
              angle: null,
            },
            line: {
              x1: null,
              y1: null,
              x2: null,
              y2: null,
            },
          },
          included_instance_types: {
            box: false,
            polygon: false,
            cuboid: false,
            ellipse: false,
            point: false,
            line: false,
          },
          is_open: false,
          el: 1,
          pre_labeled_data: null,
          file_list_to_upload: [],
          valid_points_values_polygon: false,
          valid_points_values_point_instance_type: {x: false, y: false},
          valid_points_values_box_instance_type: {x_min: false, x_max: false, y_min: false, y_max: false},
          valid_points_values_line_instance_type: {x1: false, y1: false, x2: false, y2: false},
          valid_points_values_ellipse_instance_type: {
            center_x: false,
            center_y: false,
            width: false,
            height: false,
            angle: false,
          },
          valid_points_values_cuboid_instance_type: {
            front_face_bottom_left_x: false,
            front_face_bottom_left_y: false,
            front_face_bottom_right_x: false,
            front_face_bottom_right_y: false,
            front_face_top_left_x: false,
            front_face_top_left_y: false,
            front_face_top_right_x: false,
            front_face_top_right_y: false,

            rear_face_bottom_left_x: false,
            rear_face_bottom_left_y: false,
            rear_face_bottom_right_x: false,
            rear_face_bottom_right_y: false,
            rear_face_top_left_x: false,
            rear_face_top_left_y: false,
            rear_face_top_right_x: false,
            rear_face_top_right_y: false

          },
          pre_labels_file_list: [],
          pre_label_key_list: [],
          errors_file_schema: {},
          pre_labels_file_type: null,
          errors_instance_schema: {},
          error_polygon_instance: {},
          error_point_instance: {x: {}, y: {}},
          error_line_instance: {x1: {}, y1: {}, x2: {}, y2: {}},
          error_box_instance: {x_min: {}, x_max: {}, y_min: {}, y_max: {}},
          error_cuboid_instance: {
            front_face_bottom_left_x: {},
            front_face_bottom_left_y: {},
            front_face_bottom_right_x: {},
            front_face_bottom_right_y: {},
            front_face_top_left_x: {},
            front_face_top_left_y: {},
            front_face_top_right_x: {},
            front_face_top_right_y: {},

            rear_face_bottom_left_x: {},
            rear_face_bottom_left_y: {},
            rear_face_bottom_right_x: {},
            rear_face_bottom_right_y: {},
            rear_face_top_left_x: {},
            rear_face_top_left_y: {},
            rear_face_top_right_x: {},
            rear_face_top_right_y: {}

          },
          error_ellipse_instance: {
            center_x: {},
            center_y: {},
            width: {},
            height: {},
            angle: {},
          },
        }


      },
      computed: {
        selected_polygon_key_has_nested_valued: function () {
          if (!this.diffgram_schema_mapping.polygon.points) {
            return false
          }
          for (const elm in this.pre_labeled_data) {
            const pointsValue = elm[this.diffgram_schema_mapping.polygon.points];
            if (typeof pointsValue === 'object' && pointsValue !== null) {
              return true
            } else {
              return false;
            }
          }
          return false
        },
        instance_type_schema_is_set: function () {
          return this.diffgram_schema_mapping.instance_type != null;
        },
        file_name_schema_is_set: function () {
          return this.diffgram_schema_mapping.file_name != null;
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
                this.emit('complete', file);
                this.emit('success', file);

              });
              this.on('removedfile', function (file) {
                $vm.pre_labels_file_list.splice($vm.pre_labels_file_list.indexOf(file), 1);
                $vm.pre_labeled_data = null;
                $vm.pre_label_key_list = [];
              });
            },
            url: '/api/walrus/project/' + this.project_string_id + '/upload/large',
            chunking: true,
            addRemoveLinks: true,
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
        upload_raw_media: async function(file_list){
          console.log('UPLOAD RAW MEDIA', file_list)
          this.$refs.new_or_update_upload_screen.upload_raw_media(file_list);
        },
        load_annotations_file: async function () {
          const file = this.file_list_to_upload.filter(f => f.data_type === 'Annotations')[0];
          const textData = await file.text();
          if (file.type === 'application/json') {
            this.pre_labels_file_type = 'json';
            this.pre_labeled_data = JSON.parse(textData);
            const pre_label_keys = this.extract_pre_label_key_list(this.pre_labeled_data);
            this.pre_label_key_list = [...pre_label_keys];
            this.pre_labels_file_list.push(file);
          } else if (file.type === 'text/csv') {
            this.pre_labels_file_type = 'csv';
          }
          this.el = 2;
        },
        file_list_updated: function (new_file_list) {
          this.file_list_to_upload = new_file_list;
        },
        close: function () {
          this.is_open = false;
        },

        check_box_key_structure: function (key_name) {
          this.error_box_instance = {
            x_max: {},
            y_max: {},
            x_min: {},
            y_min: {},
          };
          this.valid_points_values_box_instance_type = {
            x_max: false,
            y_max: false,
            x_min: false,
            y_min: false,
          };
          if (!this.diffgram_schema_mapping.box[key_name]) {
            throw new Error('Invalid key name for Diffgram Schema Mapping.')
            return
          } else {
            const key_name_local = this.diffgram_schema_mapping.box[key_name];
            const box_labels = this.pre_labeled_data.filter(inst => inst.type === 'box');
            for (const box_instance of box_labels) {
              if (isNaN(box_instance[key_name_local])) {
                this.error_box_instance[key_name][key_name_local] = 'Value should be a number';
                this.error_box_instance[key_name]['wrong_data'] = JSON.stringify(box_instance[key_name_local]);
                return
              }
            }
            this.valid_points_values_box_instance_type[key_name] = true;
          }
        },
        check_ellipse_key_structure: function (key_name) {
          this.error_ellipse_instance = {
            center_x: {},
            center_y: {},
            width: {},
            height: {},
            angle: {},
          };
          this.valid_points_values_ellipse_instance_type = {
            center_x: false,
            center_y: false,
            width: false,
            height: false,
            angle: false,
          };
          if (!this.diffgram_schema_mapping.ellipse[key_name]) {
            throw new Error('Invalid key name for Diffgram Schema Mapping.')
            return
          } else {
            const key_name_local = this.diffgram_schema_mapping.ellipse[key_name];
            const ellipse_labels = this.pre_labeled_data.filter(inst => inst.type === 'ellipse');
            for (const ellipse_instance of ellipse_labels) {
              if (isNaN(ellipse_instance[key_name_local])) {
                this.error_ellipse_instance[key_name][key_name_local] = 'Value should be a number';
                this.error_ellipse_instance[key_name]['wrong_data'] = JSON.stringify(ellipse_instance[key_name_local]);
                return
              }
            }
            this.valid_points_values_ellipse_instance_type[key_name] = true;
          }
        },
        check_cuboid_key_structure: function (key_name) {
          this.error_cuboid_instance = {
            front_face_bottom_left_x: {},
            front_face_bottom_left_y: {},
            front_face_bottom_right_x: {},
            front_face_bottom_right_y: {},
            front_face_top_left_x: {},
            front_face_top_left_y: {},
            front_face_top_right_x: {},
            front_face_top_right_y: {},

            rear_face_bottom_left_x: {},
            rear_face_bottom_left_y: {},
            rear_face_bottom_right_x: {},
            rear_face_bottom_right_y: {},
            rear_face_top_left_x: {},
            rear_face_top_left_y: {},
            rear_face_top_right_x: {},
            rear_face_top_right_y: {}

          };
          this.valid_points_values_cuboid_instance_type = {
            front_face_bottom_left_x: false,
            front_face_bottom_left_y: false,
            front_face_bottom_right_x: false,
            front_face_bottom_right_y: false,
            front_face_top_left_x: false,
            front_face_top_left_y: false,
            front_face_top_right_x: false,
            front_face_top_right_y: false,

            rear_face_bottom_left_x: false,
            rear_face_bottom_left_y: false,
            rear_face_bottom_right_x: false,
            rear_face_bottom_right_y: false,
            rear_face_top_left_x: false,
            rear_face_top_left_y: false,
            rear_face_top_right_x: false,
            rear_face_top_right_y: false

          };
          if (!this.diffgram_schema_mapping.cuboid[key_name]) {
            throw new Error('Invalid key name for Diffgram Schema Mapping.')
            return
          } else {
            const key_name_local = this.diffgram_schema_mapping.cuboid[key_name];
            const cuboid_labels = this.pre_labeled_data.filter(inst => inst.type === 'cuboid');
            for (const cuboid_instance of cuboid_labels) {
              if (isNaN(cuboid_instance[key_name_local])) {
                this.error_cuboid_instance[key_name][key_name_local] = 'Value should be a number';
                this.error_cuboid_instance[key_name]['wrong_data'] = JSON.stringify(cuboid_instance[key_name_local]);
                return
              }
            }
            this.valid_points_values_cuboid_instance_type[key_name] = true;
          }
        },
        check_line_key_structure: function (key_name) {
          this.error_line_instance = {x1: {}, y1: {}, x2: {}, y2: {}};
          this.valid_points_values_point_instance_type[key_name] = false;
          if (!this.diffgram_schema_mapping.line[key_name]) {
            throw new Error('Invalid key name for Diffgram Schema Mapping.')
            return
          } else {
            const key_name_local = this.diffgram_schema_mapping.line[key_name];
            const line_labels = this.pre_labeled_data.filter(inst => inst.type === 'line');
            for (const line_instance of line_labels) {
              if (isNaN(line_instance[key_name_local])) {
                this.error_line_instance[key_name][key_name_local] = 'Value should be a number';
                this.error_line_instance[key_name]['wrong_data'] = JSON.stringify(line_instance[key_name_local]);
                return
              }
            }
            this.valid_points_values_line_instance_type[key_name] = true;
          }
        },
        check_points_key_structure: function (key_name) {
          this.error_point_instance = {x: {}, y: {}};
          this.valid_points_values_point_instance_type[key_name] = false;
          if (!this.diffgram_schema_mapping.point[key_name]) {
            throw new Error('Invalid key name for Diffgram Schema Mapping.')
            return
          } else {
            const key_name_local = this.diffgram_schema_mapping.point[key_name];
            const point_labels = this.pre_labeled_data.filter(inst => inst.type === 'point');
            for (const point_instance of point_labels) {
              if (isNaN(point_instance[key_name_local])) {
                this.error_point_instance[key_name][key_name_local] = 'Value should be a number';
                this.error_point_instance[key_name]['wrong_data'] = JSON.stringify(point_instance[key_name_local]);
                return
              }
            }
            this.valid_points_values_point_instance_type[key_name] = true;
          }
        },
        check_polygon_points_key_structure() {
          this.error_polygon_instance = {}
          this.valid_points_values_polygon = false
          if (!this.diffgram_schema_mapping.polygon.points) {
            return
          } else {
            const key_name = this.diffgram_schema_mapping.polygon.points;
            const polygon_labels = this.pre_labeled_data.filter(inst => inst.type === 'polygon');
            let i = 0;
            for (const polygon_instance of polygon_labels) {
              const value = polygon_instance[key_name];
              if (!Array.isArray(value)) {
                this.error_polygon_instance['points'] = 'Points should have an array of X,Y values objects({x: number, y: number})';
                return
              }
              for (const point of value) {
                if ((!point.x || isNaN(point.x)) || (!point.y || isNaN(point.y))) {
                  this.error_polygon_instance['points'] = 'Points should have an array of X,Y values objects({x: number, y: number})'
                  this.error_polygon_instance['row_number'] = i
                  this.error_polygon_instance['data'] = JSON.stringify(polygon_instance[key_name_local]);
                  return
                }
              }

              i += 1;
            }
            this.valid_points_values_polygon = true;
          }
        },
        check_errors_and_go_to_step(step) {
          if (step === 3) {
            this.errors_file_schema = {}
            this.get_included_instance_types();
            if (!this.diffgram_schema_mapping.file_name) {
              this.errors_file_schema['file_name'] = 'Must set the file name key mapping to continue.'
              return
            }
            if (Object.keys(this.errors_file_schema).length === 0) {
              this.el = step;
            }
          } else if (step === 4) {
            this.errors_instance_schema = undefined;
            console.log('errors_instance_schema', this.errors_instance_schema)
            for (const instance_key in this.included_instance_types) {
              if (this.included_instance_types[instance_key]) {
                for (const schema_key in this.diffgram_schema_mapping[instance_key]) {
                  if (!this.diffgram_schema_mapping[instance_key][schema_key]) {
                    this.errors_instance_schema = {}
                    this.errors_instance_schema[instance_key] = `${schema_key} key is missing. Please fill out the value.`
                    return
                  }
                }
              }
            }
            this.el = step


          }

        },
        get_included_instance_types: function () {
          this.errors_file_schema = {};
          for (const elm of this.pre_labeled_data) {
            if (elm[this.diffgram_schema_mapping.instance_type]) {

              const instance_type = elm[this.diffgram_schema_mapping.instance_type];
              if (this.allowed_instance_types.includes(instance_type)) {
                this.included_instance_types[instance_type] = true;
              } else {
                this.errors_file_schema[instance_type] = `Invalid instance type "${instance_type}"`;
              }

            }
          }
        },
        extract_pre_label_key_list: function (pre_labels_object) {
          const result = []
          for (const elm of pre_labels_object) {
            for (const key in elm) {
              if (!result.includes(key)) {
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

