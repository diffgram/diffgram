<template>
  <v-container fluid>
    <v_error_multiple :error="errors_instance_schema">
    </v_error_multiple>
    <v-layout class="d-flex flex-column justify-center align-center pa-10">
      <h1 class="secondary--text">
        <strong>
          <v-icon large color="secondary">mdi-label-multiple</v-icon>
          Let's map your Label Instances!</strong>
      </h1>
      <p class="secondary--text">
        <strong>
          The following questions will guide you towards the mapping of your JSON or CSV file to Diffgram's
          spacial types.
        </strong>
      </p>
      <v-container fluid v-if="diffgram_schema_mapping" class="d-flex flex-column pa-0">
        <v-fade-transition :group="true" hide-on-leave leave-absolute>
          <div key="1" v-if="current_key === 'box'"
               class="d-flex justify-center align-center">
            <v-layout>
              <v-row>
                <v-col cols="8">
                  <div class="d-flex flex-column justify-start">
                    <h1>We've Detected box Instances!</h1>
                    <h1 class="pa-2 black--text">Please map the values of the coordinates below.:</h1>
                    <v-data-table :headers="schema_match_headers" dense :hide-default-footer="true">
                      <template v-slot:body="{ items }">
                        <tbody>
                        <tr v-for="key in Object.keys(diffgram_schema_mapping.box)">
                          <td><strong>{{key}}:</strong></td>
                          <td>
                            {{get_preview_data_for_key('box', key)}}
                          </td>
                          <td class="d-flex align-center">
                            <v-autocomplete class="pt-4"
                                            style="max-width: 200px"
                                            dense
                                            @change="check_box_key_structure(key)"
                                            :items="pre_label_key_list_filtered"
                                            v-model="diffgram_schema_mapping.box[key]">

                            </v-autocomplete>
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
                  </div>
                </v-col>
                <v-col cols="4">
                  <img src="https://storage.googleapis.com/diffgram-002/public/image/box.png"/>
                </v-col>
              </v-row>
            </v-layout>
          </div>
        </v-fade-transition>
        <v-fade-transition :group="true" hide-on-leave leave-absolute>
          <div key="2" v-if="current_key === 'polygon'"
               class="d-flex justify-center align-center">
            <v-layout>
              <v-row>
                <v-col cols="8">
                  <div class="d-flex flex-column justify-start">
                    <h1>We've Detected Polygon Instances!</h1>
                    <h1 class="pa-2 black--text">Please map the values of the coordinates below.:</h1>
                    <v-data-table :headers="schema_match_headers" dense :hide-default-footer="true">
                      <template v-slot:body="{ items }">
                        <tbody>

                        <tr v-if="pre_labels_file_type === 'json'">
                          <td><strong>points:</strong></td>
                          <td>
                            {{get_preview_data_for_key('polygon', 'points')}}
                          </td>
                          <td class="d-flex align-center">
                            <v-autocomplete class="pt-4"
                                      style="max-width: 200px"
                                      dense
                                      :items="pre_label_key_list_filtered"
                                      @change="check_polygon_points_key_structure"
                                      v-model="diffgram_schema_mapping.polygon.points">

                            </v-autocomplete>
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
                        <tr v-if="pre_labels_file_type === 'csv'">
                          <td><strong>points X:</strong></td>
                          <td>
                            {{get_preview_data_for_key('polygon', 'points_x')}}
                          </td>
                          <td class="d-flex align-center">
                            <v-autocomplete class="pt-4"
                                      style="max-width: 200px"
                                      dense
                                      :items="pre_label_key_list_filtered"
                                      @change="check_polygon_points_key_structure"
                                      v-model="diffgram_schema_mapping.polygon.points_x">

                            </v-autocomplete>
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
                                values. The values inside each column should be separated by ';'.
                              </strong>
                            </p>
                          </td>
                        </tr>
                        <tr v-if="pre_labels_file_type === 'csv'">
                          <td><strong>points Y:</strong></td>
                          <td>
                            {{get_preview_data_for_key('polygon', 'points_y')}}
                          </td>
                          <td class="d-flex align-center">
                            <v-autocomplete class="pt-4"
                                      style="max-width: 200px"
                                      dense
                                      :items="pre_label_key_list_filtered"
                                      @change="check_polygon_points_key_structure"
                                      v-model="diffgram_schema_mapping.polygon.points_y">

                            </v-autocomplete>
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
                                values. The values inside each column should be separated by ';'.
                              </strong>
                            </p>
                          </td>
                        </tr>
                        </tbody>
                      </template>
                    </v-data-table>
                  </div>
                </v-col>
                <v-col cols="4">
                  <img width="700px" src="https://storage.googleapis.com/diffgram-002/public/image/polygon.png"/>
                </v-col>
              </v-row>
            </v-layout>
          </div>
        </v-fade-transition>
        <v-fade-transition :group="true" hide-on-leave leave-absolute>
          <div key="3" v-if="current_key === 'cuboid'"
               class="d-flex justify-center align-center">
            <v-layout>
              <v-row>
                <v-col cols="8">
                  <div class="d-flex flex-column justify-start">
                    <h1>We've Detected Cuboid Instances!</h1>
                    <h1 class="pa-2 black--text">Please map the values of the coordinates below.:</h1>
                    <v-data-table style="height: 430px; overflow-y: scroll;" :headers="schema_match_headers" dense :hide-default-footer="true">
                      <template v-slot:body="{ items }">
                        <tbody>
                        <tr v-for="key in Object.keys(diffgram_schema_mapping.cuboid)">
                          <td><strong>{{key}}:</strong></td>
                          <td>
                            {{get_preview_data_for_key('cuboid', key)}}
                          </td>
                          <td class="d-flex align-center">
                            <v-autocomplete class="pt-4"
                                      style="max-width: 200px"
                                      dense
                                      @change="check_cuboid_key_structure(key)"
                                      :items="pre_label_key_list_filtered"
                                      v-model="diffgram_schema_mapping.cuboid[key]">
                            </v-autocomplete>
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
                  </div>
                </v-col>
                <v-col cols="4">
                  <img width="700px" src="https://storage.googleapis.com/diffgram-002/public/image/cuboid.png"/>
                </v-col>
              </v-row>
            </v-layout>
          </div>
        </v-fade-transition>
        <v-fade-transition :group="true" hide-on-leave leave-absolute>
          <div key="4" v-if="current_key === 'point'"
               class="d-flex justify-center align-center">
            <v-layout>
              <v-row>
                <v-col cols="8">
                  <div class="d-flex flex-column justify-start">
                    <h1>We've Detected Point Instances!</h1>
                    <h1 class="pa-2 black--text">Please map the values of the coordinates below.:</h1>
                    <v-data-table :headers="schema_match_headers" dense :hide-default-footer="true">
                      <template v-slot:body="{ items }">
                        <tbody>
                        <tr v-for="key in Object.keys(diffgram_schema_mapping.point)">
                          <td><strong>point {{key}} value:</strong></td>
                          <td>
                            {{get_preview_data_for_key('point', key)}}
                          </td>
                          <td>
                            <v-autocomplete class="pt-4"
                                      style="max-width: 200px"
                                      dense
                                      :items="pre_label_key_list_filtered"
                                      @change="check_points_key_structure(key)"
                                      v-model="diffgram_schema_mapping.point[key]">

                            </v-autocomplete>
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
                  </div>
                </v-col>
                <v-col cols="4">
                  <img width="300px" src="https://storage.googleapis.com/diffgram-002/public/image/point.png"/>
                </v-col>
              </v-row>
            </v-layout>
          </div>
        </v-fade-transition>
        <v-fade-transition :group="true" hide-on-leave leave-absolute>
          <div key="5" v-if="current_key === 'line'"
               class="d-flex justify-center align-center">
            <v-layout>
              <v-row>
                <v-col cols="8">
                  <div class="d-flex flex-column justify-start">
                    <h1>We've Detected Line Instances!</h1>
                    <h1 class="pa-2 black--text">Please map the values of the coordinates below.:</h1>
                    <v-data-table :headers="schema_match_headers" dense :hide-default-footer="true">
                      <template v-slot:body="{ items }">
                        <tbody>
                        <tr v-for="key in Object.keys(diffgram_schema_mapping.line)">
                          <td><strong>line {{key}} value:</strong></td>
                          <td>
                            {{get_preview_data_for_key('line', key)}}
                          </td>
                          <td class="d-flex align-center">
                            <v-autocomplete class="pt-4"
                                      style="max-width: 200px"
                                      dense
                                      @change="check_line_key_structure(key)"
                                      :items="pre_label_key_list_filtered"
                                      v-model="diffgram_schema_mapping.line[key]">

                            </v-autocomplete>
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
                  </div>
                </v-col>
                <v-col cols="4">
                  <img width="600px" src="https://storage.googleapis.com/diffgram-002/public/image/line.png"/>
                </v-col>
              </v-row>
            </v-layout>
          </div>
        </v-fade-transition>
        <v-fade-transition :group="true" hide-on-leave leave-absolute>
          <div key="5" v-if="current_key === 'ellipse'"
               class="d-flex justify-center align-center">
            <v-layout>
              <v-row>
                <v-col cols="8">
                  <div class="d-flex flex-column justify-start">
                    <h1>We've Detected Ellipse Instances!</h1>
                    <h1 class="pa-2 black--text">Please map the values of the coordinates below.:</h1>
                    <v-data-table :headers="schema_match_headers" dense :hide-default-footer="true">
                      <template v-slot:body="{ items }">
                        <tbody>
                        <tr v-for="key in Object.keys(diffgram_schema_mapping.ellipse)">
                          <td><strong>{{key}}:</strong></td>
                          <td>
                            {{get_preview_data_for_key('ellipse', key)}}
                          </td>
                          <td class="d-flex align-center">
                            <v-autocomplete class="pt-4"
                                      style="max-width: 200px"
                                      dense
                                      @change="check_ellipse_key_structure(key)"
                                      :items="pre_label_key_list_filtered"
                                      v-model="diffgram_schema_mapping.ellipse[key]">

                            </v-autocomplete>
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
                  </div>
                </v-col>
                <v-col cols="4">
                  <img width="600px" src="https://storage.googleapis.com/diffgram-002/public/image/ellipse.png"/>
                </v-col>
              </v-row>
            </v-layout>
          </div>
        </v-fade-transition>
      </v-container>
    </v-layout>
    <v-layout class="d-flex justify-space-between" v-if="current_question != 6">
      <v-btn x-large
             :loading="loading"
             :disabled="current_question === 1"
             class="primary lighten-4 ma-8"
             style="justify-self: start"
             @click="previous_step(current_question)">
        Back
      </v-btn>
      <v-btn x-large
             style="justify-self: end"
             :loading="loading"
             class="primary ma-8"
             @click="next_step(current_question)">
        Continue
      </v-btn>
    </v-layout>
  </v-container>

</template>

<script lang="ts">
  import axios from 'axios';
  import Vue from "vue";
  import {v4 as uuidv4} from 'uuid';
  import filesize from 'filesize';

  export default Vue.extend({
      name: 'instance_schema_mapper',
      components: {},
      props: {
        'project_string_id': {
          default: null
        },
        'file_list_to_upload': {
          default: null
        },
        'upload_mode': {
          default: 'new'
        },
        'supported_video_files': {
          default: () => ['video/mp4', 'video/x-msvideo', 'video/quicktime', 'video/x-m4v'],
        },
        'pre_label_key_list': {
          default: () => []
        },
        'diffgram_schema_mapping': {
          default: null
        },
        'included_instance_types': {
          default: null
        },
        'pre_labeled_data': {
          default: null
        },
        'pre_labels_file_type': {
          default: null
        },
        'previously_completed_questions':{
          default: 0
        }
      },
      data() {
        return {
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
          allowed_instance_types: [
            'box',
            'polygon',
            'line',
            'point',
            'cuboid',
            'ellipse',
          ],
          loading: false,
          current_question: 0,
          errors_instance_schema: undefined,
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
        }
      },
      computed: {
        current_key: function(){
          return Object.keys(this.$props.included_instance_types).filter(key => this.$props.included_instance_types[key] === true)[this.current_question];
        },
        selected_keys: function () {
          const result = [];
          for (const key of Object.keys(this.diffgram_schema_mapping)) {
            if (this.diffgram_schema_mapping[key] && typeof this.diffgram_schema_mapping[key] !== 'object') {
              result.push(this.diffgram_schema_mapping[key])
            }
            else if (['point', 'polygon', 'ellipse', 'line', 'cuboid', 'box'].includes(key)){
              for(const subkey of Object.keys(this.diffgram_schema_mapping[key])){
                if (this.diffgram_schema_mapping[key][subkey]) {
                  result.push(this.diffgram_schema_mapping[key][subkey])
                }
              }
            }

          }
          return result;
        },
        pre_label_key_list_filtered: function () {
          return this.pre_label_key_list.map(key => ({
            text: key,
            value: key,
            disabled: this.selected_keys.includes(key)
          }));
        }
      },
      watch: {},
      mounted() {
      },
      created() {
      },
      beforeDestroy() {

      },
      methods: {
        previous_step: async function (current_number) {
          const old_number = parseInt(current_number, 10);
          this.current_question = undefined;
          await this.$nextTick();
          await new Promise(resolve => setTimeout(resolve, 500));
          await this.$nextTick();
          if(old_number >= 0){
            this.current_question = old_number - 1;
          }
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
        check_for_videos_in_uploaded_files: function () {
          for (const file of this.$props.file_list_to_upload) {
            if (this.supported_video_files.includes(file.type)) {
              return true
            }
          }
          return false;
        },
        validate_model_id: function () {
          // Nothing to validate for now
          return true;
        },
        validate_mode_run_id: function () {
          // Nothing to validate for now.
          return true
        },
        get_preview_data_for_key: function (instance_type, key) {
          if (!instance_type || !key) {
            return ''
          }
          let result = '';
          for (const instance of this.pre_labeled_data) {
            let value = instance[this.diffgram_schema_mapping[instance_type][key]];
            if(typeof value === "object"){
              value = JSON.stringify(instance[this.diffgram_schema_mapping[instance_type][key]]);
            }
            if (value) {
              result += `${value}, \n`
            }
          }
          return result
        },
        build_points_for_polygon() {
          if (this.$props.pre_labels_file_type === 'json') {
            return true
          }
          if (!this.diffgram_schema_mapping.polygon.points_x || !this.diffgram_schema_mapping.polygon.points_y) {
            return false
          }
          for (const instance of this.pre_labeled_data) {
            let x_points = instance[this.diffgram_schema_mapping.polygon.points_x];
            x_points = x_points.split(';').map(x => parseInt(x, 10))
            let y_points = instance[this.diffgram_schema_mapping.polygon.points_y];
            y_points = y_points.split(';').map(y => parseInt(y, 10))
            if (!x_points || !y_points) {
              this.errors_instance_schema = {};
              this.errors_instance_schema['points'] = 'Provide X, Y point values.';
              this.errors_instance_schema['wrong_data'] = JSON.stringify(instance);
              return false
            }
            if (x_points.length !== y_points.length) {
              this.errors_instance_schema = {};
              this.errors_instance_schema['x_points'] = 'X and Y values must be the same length';
              this.errors_instance_schema['wrong_data'] = JSON.stringify(instance);
              return false
            }
            instance.points = []
            for (let i = 0; i < x_points.length; i++) {
              instance.points.push({
                x: x_points[i],
                y: y_points[i],
              })
            }
            // Automatically map to 'points' value of the instance.
            this.diffgram_schema_mapping.polygon.points = 'points';

          }
          return true;
        },
        next_step: async function (current_number, validate_data = true) {
          let valid = false;
          let loading = true;
          const num_types = Object.keys(this.$props.included_instance_types).filter(key => this.$props.included_instance_types[key] === true).length;
          const old_number = parseInt(current_number, 10);

          await this.$nextTick();
          await new Promise(resolve => setTimeout(resolve, 500));
          await this.$nextTick();
          this.errors_instance_schema = undefined;

          if(this.current_key === 'polygon'){
            valid = this.build_points_for_polygon()

          }
          else{
            valid = true;
          }
          if (this.included_instance_types[this.current_key]) {
            for (const schema_key in this.diffgram_schema_mapping[this.current_key]) {
              if (!this.diffgram_schema_mapping[this.current_key][schema_key]
                && this.current_key === 'polygon'
                && ['points_x', 'points_y'].includes(schema_key)
                && this.$props.pre_labels_file_type === 'json') {
                // Skip polygon x,y points when pre_labels are in json format.
                continue
              }
              if (!this.diffgram_schema_mapping[this.current_key][schema_key]) {
                this.errors_instance_schema = {}
                this.errors_instance_schema[this.current_key] = `${schema_key} key is missing. Please fill out the value.`
                valid = false
              }
            }
          }

          if (valid) {

            if(current_number === num_types - 1){
              this.$emit('change_step_wizard');
              this.current_question = old_number + 1;
            }
            else{
              this.current_question = old_number + 1;
            }

            this.$emit('complete_question', this.current_question + this.$props.previously_completed_questions)

          } else {
            this.current_question = old_number;
          }
          this.loading = false;
        },
      }
    }
  ) </script>

<style>

</style>
