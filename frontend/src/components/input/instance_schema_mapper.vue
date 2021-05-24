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
      <v-container fluid v-if="diffgram_schema_mapping" class="d-flex flex-column pa-0" style="height: 500px">
        <v-fade-transition :group="true" hide-on-leave leave-absolute>
          <div key="1" v-if="current_question === 1 && included_instance_types.box" class="d-flex justify-center align-center">
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
                                      :items="pre_label_key_list"
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
        <v-fade-transition v-if="false" :group="true" hide-on-leave>
          <h1 class="pa-10 black--text">Match Fields to Diffgram Schema</h1>
          <v-expansion-panels accordion>
            <v-expansion-panel key="box" class="ma-4" v-if="included_instance_types.box">
              <v-expansion-panel-header color="primary lighten-2" class="text--white">
                <span class="white--text"><strong>Box Type (Click to match schema)</strong></span>
              </v-expansion-panel-header>
              <v-expansion-panel-content>
                <v-layout class="d-flex column">

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
                        {{get_preview_data_for_key('polygon', 'points')}}
                      </td>
                      <td class="d-flex align-center">
                        <v-autocomplete class="pt-4"
                                  style="max-width: 200px"
                                  dense
                                  :items="pre_label_key_list"
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
                                  :items="pre_label_key_list"
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
                                  :items="pre_label_key_list"
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
                        {{get_preview_data_for_key('point', key)}}
                      </td>
                      <td>
                        <v-autocomplete class="pt-4"
                                  style="max-width: 200px"
                                  dense
                                  :items="pre_label_key_list"
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
                        {{get_preview_data_for_key('line', key)}}
                      </td>
                      <td class="d-flex align-center">
                        <v-autocomplete class="pt-4"
                                  style="max-width: 200px"
                                  dense
                                  @change="check_line_key_structure(key)"
                                  :items="pre_label_key_list"
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
                        {{get_preview_data_for_key('cuboid', key)}}
                      </td>
                      <td class="d-flex align-center">
                        <v-autocomplete class="pt-4"
                                  style="max-width: 200px"
                                  dense
                                  @change="check_cuboid_key_structure(key)"
                                  :items="pre_label_key_list"
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
                        {{get_preview_data_for_key('ellipse', key)}}
                      </td>
                      <td class="d-flex align-center">
                        <v-autocomplete class="pt-4"
                                  style="max-width: 200px"
                                  dense
                                  @change="check_ellipse_key_structure(key)"
                                  :items="pre_label_key_list"
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
              </v-expansion-panel-content>
            </v-expansion-panel>
          </v-expansion-panels>
          <div class="d-flex justify-end">
            <v_error_multiple dense :error="errors_instance_schema">
            </v_error_multiple>
            <v-btn @click="check_errors_and_go_to_step(4)" color="primary" x-large> Continue</v-btn>
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
        'file_list_to_upload':{
          default: null
        },
        'upload_mode': {
          default: 'new'
        },
        'supported_video_files':{
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
          current_question: 1,
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
      computed: {},
      watch: {},
      mounted() {
      },
      created() {
      },
      beforeDestroy() {

      },
      methods: {
        previous_step: async function(current_number){
          const old_number = parseInt(current_number, 10);
          this.current_question = undefined;
          await this.$nextTick();
          await new Promise(resolve => setTimeout(resolve, 500));
          await this.$nextTick();
          this.current_question = old_number - 1;
        },
        check_for_videos_in_uploaded_files: function(){
          for(const file of this.$props.file_list_to_upload){
            if(this.supported_video_files.includes(file.type)){
              return true
            }
          }
          return false;
        },
        validate_model_id: function(){
          // Nothing to validate for now
          return true;
        },
        validate_mode_run_id: function(){
          // Nothing to validate for now.
          return true
        },
        get_preview_data_for_key: function (instance_type, key) {
          if (!instance_type || !key) {
            return ''
          }
          let result = '';
          for (const instance of this.pre_labeled_data) {
            const value = instance[this.diffgram_schema_mapping[instance_type][key]];
            if (value) {
              result += `${value}, \n`
            }
          }
          return result
        },
        next_step: async function (current_number, validate_data = true) {
          let valid = false;
          let loading = true;
          const old_number = parseInt(current_number, 10);
          this.current_question = undefined;
          await this.$nextTick();
          await new Promise(resolve => setTimeout(resolve, 500));
          await this.$nextTick();
          this.errors_instance_schema = undefined;

          if (current_number === 1) {
            valid = this.get_included_instance_types();
          } else if (current_number === 2) {
            valid = await this.validate_label_names();
          } else if (current_number === 3) {
            if (this.$props.upload_mode === 'new') {
              valid = this.validate_file_names();
            } else if (this.$props.upload_mode === 'update') {
              valid = await this.validate_file_id_list_for_update();
            } else {
              throw Error('Invalid upload mode.')
              valid = false;
            }
          }
          else if(current_number === 4){
            // Validate frame numbers
            valid = this.validate_frames();
            console.log('framess', valid)
          }
          else if(current_number === 5){
            // Validate frame sequences
            valid = this.validate_sequences();
          }
          else if(current_number === 6){
            valid = true;
          }
          else if(current_number === 7 ){
            valid = this.validate_model_id();
          }
          else if(current_number === 8){
            valid = this.validate_mode_run_id();
          }

          if (valid) {
            if(current_number === 3){
              // Check for the existence of Videos.
              const has_video = this.check_for_videos_in_uploaded_files();
              if(has_video){
                this.current_question = old_number + 1;
                return
              }
              else{
                this.current_question = old_number + 3;
                return
              }
            }
            if(current_number === 8){
              this.$emit('change_step_wizard')
              this.current_question = old_number;
              return
            }
            this.current_question = old_number + 1;
          }
          else{
            this.current_question = old_number;
          }
          this.loading = false;
        },
      }
    }
  ) </script>

<style>

</style>
