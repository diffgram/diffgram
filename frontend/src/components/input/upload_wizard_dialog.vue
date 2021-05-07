<template>

  <v-dialog v-model="is_open" width="1500px" id="task-input-list-dialog" style="min-height: 800px" persistent>
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
          step="2"
        >
          Upload Prelabled Data
        </v-stepper-step>

        <v-divider></v-divider>
        <v-stepper-step
          editable
          :complete="el > 3"
          step="3">
          Prepare Prelabeled Data
        </v-stepper-step>
        <v-stepper-step
          editable
          :complete="el > 4"
          step="4">
          Match data to Diffgram Schema
        </v-stepper-step>
        <v-divider></v-divider>
        <v-stepper-step :complete="el > 5" step="5" editable>
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
          <v-layout class="d-flex flex-column justify-center align-center pa-10">

            <v_error_multiple :error="error_instance_type">
            </v_error_multiple>
            <v-container class="d-flex flex-column pa-0">
              <div class="d-flex justify-start align-center">
                <div class="d-flex flex-column justify-start">
                  <h3 class="pa-2 black--text">* Select the Field Corresponding to the instance type</h3>
                  <p style="font-size: 12px" class="primary--text text--lighten-3"><strong>** Note: Allowed values here are: {{allowed_instance_types}}</strong></p>

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
                  <h3 class="pa-2 black--text">Select the Field Corresponding to the Model ID (Optional)</h3>
                  <p style="font-size: 12px" class="primary--text text--lighten-3"><strong>If model already exists, instances will be binded to existing model.</strong></p>

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
                  <p style="font-size: 12px" class="primary--text text--lighten-3"><strong>If the run already exists, instances will be binded to existing run.</strong></p>

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
                   :disabled="!instance_type_schema_is_set"
                   @click="check_errors_and_go_to_step(4)">
              Continue
            </v-btn>
          </v-layout>
        </v-stepper-content>

        <v-stepper-content step="4">
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
                      <tr>
                        <td><strong>x_max:</strong></td>
                        <td>
                          Preview Data Here
                        </td>
                        <td class="d-flex align-center">
                          <v-select class="pt-4"
                                    style="max-width: 200px"
                                    dense
                                    :items="pre_label_key_list"
                                    v-model="diffgram_schema_mapping.box.x_max">

                          </v-select>
                        </td>
                      </tr>
                      <tr>
                        <td><strong>x_min:</strong></td>
                        <td>
                          Preview Data Here
                        </td>
                        <td class="d-flex align-center">
                          <v-select class="pt-4"
                                    style="max-width: 200px"
                                    dense
                                    :items="pre_label_key_list"
                                    v-model="diffgram_schema_mapping.box.x_min">

                          </v-select>
                        </td>
                      </tr>
                      <tr>
                        <td><strong>y_max:</strong></td>
                        <td>
                          Preview Data Here
                        </td>
                        <td class="d-flex align-center">
                          <v-select class="pt-4"
                                    style="max-width: 200px"
                                    dense
                                    :items="pre_label_key_list"
                                    v-model="diffgram_schema_mapping.box.y_max">

                          </v-select>
                        </td>
                      </tr>
                      <tr>
                        <td><strong>y_min:</strong></td>
                        <td>
                          Preview Data Here
                        </td>
                        <td class="d-flex align-center">
                          <v-select class="pt-4"
                                    style="max-width: 200px"
                                    dense
                                    :items="pre_label_key_list"
                                    v-model="diffgram_schema_mapping.box.y_min">

                          </v-select>
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
                    <tr>
                      <td><strong>points:</strong></td>
                      <td>
                        Preview Data Here
                      </td>
                      <td class="d-flex align-center">
                        <v-select class="pt-4"
                                  style="max-width: 200px"
                                  dense
                                  :items="pre_label_key_list"
                                  v-model="diffgram_schema_mapping.polygon.points">

                        </v-select>
                      </td>
                    </tr>
                    <tr>
                      <td><strong>point x value:</strong></td>
                      <td>
                        Preview Data Here
                      </td>
                      <td class="d-flex align-center">
                        <v-select class="pt-4"
                                  style="max-width: 200px"
                                  dense
                                  :items="pre_label_key_list"
                                  v-model="diffgram_schema_mapping.polygon.point_x">

                        </v-select>
                      </td>
                    </tr>
                    <tr>
                      <td><strong>point y value:</strong></td>
                      <td>
                        Preview Data Here
                      </td>
                      <td class="d-flex align-center">
                        <v-select class="pt-4"
                                  style="max-width: 200px"
                                  dense
                                  :items="pre_label_key_list"
                                  v-model="diffgram_schema_mapping.polygon.point_y">

                        </v-select>
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
                    <tr>
                      <td><strong>point x value:</strong></td>
                      <td>
                        Preview Data Here
                      </td>
                      <td class="d-flex align-center">
                        <v-select class="pt-4"
                                  style="max-width: 200px"
                                  dense
                                  :items="pre_label_key_list"
                                  v-model="diffgram_schema_mapping.point.x">

                        </v-select>
                      </td>
                    </tr>
                    <tr>
                      <td><strong>point y value:</strong></td>
                      <td>
                        Preview Data Here
                      </td>
                      <td class="d-flex align-center">
                        <v-select class="pt-4"
                                  style="max-width: 200px"
                                  dense
                                  :items="pre_label_key_list"
                                  v-model="diffgram_schema_mapping.point.y">

                        </v-select>
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
                    <tr>
                      <td><strong>line x1 value:</strong></td>
                      <td>
                        Preview Data Here
                      </td>
                      <td class="d-flex align-center">
                        <v-select class="pt-4"
                                  style="max-width: 200px"
                                  dense
                                  :items="pre_label_key_list"
                                  v-model="diffgram_schema_mapping.line.x1">

                        </v-select>
                      </td>
                    </tr>
                    <tr>
                      <td><strong>line y1 value:</strong></td>
                      <td>
                        Preview Data Here
                      </td>
                      <td class="d-flex align-center">
                        <v-select class="pt-4"
                                  style="max-width: 200px"
                                  dense
                                  :items="pre_label_key_list"
                                  v-model="diffgram_schema_mapping.line.y1">

                        </v-select>
                      </td>
                    </tr>
                    <tr>
                      <td><strong>line x2 value:</strong></td>
                      <td>
                        Preview Data Here
                      </td>
                      <td class="d-flex align-center">
                        <v-select class="pt-4"
                                  style="max-width: 200px"
                                  dense
                                  :items="pre_label_key_list"
                                  v-model="diffgram_schema_mapping.line.x2">

                        </v-select>
                      </td>
                    </tr>
                    <tr>
                      <td><strong>line y2 value:</strong></td>
                      <td>
                        Preview Data Here
                      </td>
                      <td class="d-flex align-center">
                        <v-select class="pt-4"
                                  style="max-width: 200px"
                                  dense
                                  :items="pre_label_key_list"
                                  v-model="diffgram_schema_mapping.line.y2">

                        </v-select>
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
                    <tr>
                      <td><strong>front_face_bottom_left_x:</strong></td>
                      <td>
                        Preview Data Here
                      </td>
                      <td class="d-flex align-center">
                        <v-select class="pt-4"
                                  style="max-width: 200px"
                                  dense
                                  :items="pre_label_key_list"
                                  v-model="diffgram_schema_mapping.cuboid.front_face_bottom_left_x">

                        </v-select>
                      </td>
                    </tr>
                    <tr>
                      <td><strong>front_face_bottom_right_x:</strong></td>
                      <td>
                        Preview Data Here
                      </td>
                      <td class="d-flex align-center">
                        <v-select class="pt-4"
                                  style="max-width: 200px"
                                  dense
                                  :items="pre_label_key_list"
                                  v-model="diffgram_schema_mapping.cuboid.front_face_bottom_right_x">

                        </v-select>
                      </td>
                    </tr>
                    <tr>
                      <td><strong>front_face_bottom_left_y:</strong></td>
                      <td>
                        Preview Data Here
                      </td>
                      <td class="d-flex align-center">
                        <v-select class="pt-4"
                                  style="max-width: 200px"
                                  dense
                                  :items="pre_label_key_list"
                                  v-model="diffgram_schema_mapping.cuboid.front_face_bottom_left_y">

                        </v-select>
                      </td>
                    </tr>
                    <tr>
                      <td><strong>front_face_bottom_right_y:</strong></td>
                      <td>
                        Preview Data Here
                      </td>
                      <td class="d-flex align-center">
                        <v-select class="pt-4"
                                  style="max-width: 200px"
                                  dense
                                  :items="pre_label_key_list"
                                  v-model="diffgram_schema_mapping.cuboid.front_face_bottom_right_y">

                        </v-select>
                      </td>
                    </tr>
                    <tr><td colspan="4"></td></tr>
                    <tr>
                      <td><strong>front_face_top_left_x:</strong></td>
                      <td>
                        Preview Data Here
                      </td>
                      <td class="d-flex align-center">
                        <v-select class="pt-4"
                                  style="max-width: 200px"
                                  dense
                                  :items="pre_label_key_list"
                                  v-model="diffgram_schema_mapping.cuboid.front_face_top_left_x">

                        </v-select>
                      </td>
                    </tr>
                    <tr>
                      <td><strong>front_face_top_right_x:</strong></td>
                      <td>
                        Preview Data Here
                      </td>
                      <td class="d-flex align-center">
                        <v-select class="pt-4"
                                  style="max-width: 200px"
                                  dense
                                  :items="pre_label_key_list"
                                  v-model="diffgram_schema_mapping.cuboid.front_face_top_right_x">

                        </v-select>
                      </td>
                    </tr>
                    <tr>
                      <td><strong>front_face_top_left_y:</strong></td>
                      <td>
                        Preview Data Here
                      </td>
                      <td class="d-flex align-center">
                        <v-select class="pt-4"
                                  style="max-width: 200px"
                                  dense
                                  :items="pre_label_key_list"
                                  v-model="diffgram_schema_mapping.cuboid.front_face_top_left_y">

                        </v-select>
                      </td>
                    </tr>
                    <tr>
                      <td><strong>front_face_top_right_y:</strong></td>
                      <td>
                        Preview Data Here
                      </td>
                      <td class="d-flex align-center">
                        <v-select class="pt-4"
                                  style="max-width: 200px"
                                  dense
                                  :items="pre_label_key_list"
                                  v-model="diffgram_schema_mapping.cuboid.front_face_top_right_y">

                        </v-select>
                      </td>
                    </tr>
                    <tr><td colspan="4"></td></tr>
                    <tr>
                      <td><strong>rear_face_bottom_left_x:</strong></td>
                      <td>
                        Preview Data Here
                      </td>
                      <td class="d-flex align-center">
                        <v-select class="pt-4"
                                  style="max-width: 200px"
                                  dense
                                  :items="pre_label_key_list"
                                  v-model="diffgram_schema_mapping.cuboid.rear_face_bottom_left_x">

                        </v-select>
                      </td>
                    </tr>
                    <tr>
                      <td><strong>rear_face_bottom_right_x:</strong></td>
                      <td>
                        Preview Data Here
                      </td>
                      <td class="d-flex align-center">
                        <v-select class="pt-4"
                                  style="max-width: 200px"
                                  dense
                                  :items="pre_label_key_list"
                                  v-model="diffgram_schema_mapping.cuboid.rear_face_bottom_right_x">

                        </v-select>
                      </td>
                    </tr>
                    <tr>
                      <td><strong>rear_face_bottom_left_y:</strong></td>
                      <td>
                        Preview Data Here
                      </td>
                      <td class="d-flex align-center">
                        <v-select class="pt-4"
                                  style="max-width: 200px"
                                  dense
                                  :items="pre_label_key_list"
                                  v-model="diffgram_schema_mapping.cuboid.rear_face_bottom_left_y">

                        </v-select>
                      </td>
                    </tr>
                    <tr>
                      <td><strong>rear_face_bottom_right_y:</strong></td>
                      <td>
                        Preview Data Here
                      </td>
                      <td class="d-flex align-center">
                        <v-select class="pt-4"
                                  style="max-width: 200px"
                                  dense
                                  :items="pre_label_key_list"
                                  v-model="diffgram_schema_mapping.cuboid.rear_face_bottom_right_y">

                        </v-select>
                      </td>
                    </tr>
                    <tr><td colspan="4"></td></tr>
                    <tr>
                      <td><strong>rear_face_top_left_x:</strong></td>
                      <td>
                        Preview Data Here
                      </td>
                      <td class="d-flex align-center">
                        <v-select class="pt-4"
                                  style="max-width: 200px"
                                  dense
                                  :items="pre_label_key_list"
                                  v-model="diffgram_schema_mapping.cuboid.rear_face_top_left_x">

                        </v-select>
                      </td>
                    </tr>
                    <tr>
                      <td><strong>rear_face_top_right_x:</strong></td>
                      <td>
                        Preview Data Here
                      </td>
                      <td class="d-flex align-center">
                        <v-select class="pt-4"
                                  style="max-width: 200px"
                                  dense
                                  :items="pre_label_key_list"
                                  v-model="diffgram_schema_mapping.cuboid.rear_face_top_right_x">

                        </v-select>
                      </td>
                    </tr>
                    <tr>
                      <td><strong>rear_face_top_left_y:</strong></td>
                      <td>
                        Preview Data Here
                      </td>
                      <td class="d-flex align-center">
                        <v-select class="pt-4"
                                  style="max-width: 200px"
                                  dense
                                  :items="pre_label_key_list"
                                  v-model="diffgram_schema_mapping.cuboid.rear_face_top_left_y">

                        </v-select>
                      </td>
                    </tr>
                    <tr>
                      <td><strong>rear_face_top_right_y:</strong></td>
                      <td>
                        Preview Data Here
                      </td>
                      <td class="d-flex align-center">
                        <v-select class="pt-4"
                                  style="max-width: 200px"
                                  dense
                                  :items="pre_label_key_list"
                                  v-model="diffgram_schema_mapping.cuboid.rear_face_top_right_y">

                        </v-select>
                      </td>
                    </tr>

                    </tbody>
                  </template>
                </v-data-table>
              </v-expansion-panel-content>
            </v-expansion-panel>
            <v-expansion-panel key="ellipse"  class="ma-4"  v-if="included_instance_types.ellipse">
              <v-expansion-panel-header color="primary lighten-2" class="text--white">
                <span class="white--text"><strong>Ellipse Type (Click to match schema)</strong></span>
              </v-expansion-panel-header>
              <v-expansion-panel-content>
                <v-data-table :headers="schema_match_headers" dense :hide-default-footer="true">
                  <template v-slot:body="{ items }">
                    <tbody>
                    <tr>
                      <td><strong>center_x:</strong></td>
                      <td>
                        Preview Data Here
                      </td>
                      <td class="d-flex align-center">
                        <v-select class="pt-4"
                                  style="max-width: 200px"
                                  dense
                                  :items="pre_label_key_list"
                                  v-model="diffgram_schema_mapping.ellipse.center_x">

                        </v-select>
                      </td>
                    </tr>
                    <tr>
                      <td><strong>center_y:</strong></td>
                      <td>
                        Preview Data Here
                      </td>
                      <td class="d-flex align-center">
                        <v-select class="pt-4"
                                  style="max-width: 200px"
                                  dense
                                  :items="pre_label_key_list"
                                  v-model="diffgram_schema_mapping.ellipse.center_y">

                        </v-select>
                      </td>
                    </tr>
                    <tr>
                      <td><strong>width:</strong></td>
                      <td>
                        Preview Data Here
                      </td>
                      <td class="d-flex align-center">
                        <v-select class="pt-4"
                                  style="max-width: 200px"
                                  dense
                                  :items="pre_label_key_list"
                                  v-model="diffgram_schema_mapping.ellipse.width">

                        </v-select>
                      </td>
                    </tr>
                    <tr>
                      <td><strong>height:</strong></td>
                      <td>
                        Preview Data Here
                      </td>
                      <td class="d-flex align-center">
                        <v-select class="pt-4"
                                  style="max-width: 200px"
                                  dense
                                  :items="pre_label_key_list"
                                  v-model="diffgram_schema_mapping.ellipse.height">

                        </v-select>
                      </td>
                    </tr>
                    </tbody>
                  </template>
                </v-data-table>
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
            <v-btn x-large class="success ma-8" @click="start_upload">Upload to Diffgram</v-btn>
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
          schema_match_headers: [
            {
              text: 'Diffgram Value',
              align: 'start',
              sortable: false,
              value: 'diffgram_value',
            },
            { text: 'Preview Data',
              value: 'preview',
              align: 'start',
              sortable: false,
            },
            { text: 'File Value',
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
            model_id: null,
            model_rune_id: null,
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
            polygon:{
              points: null,
              point_x: null,
              point_y: null,
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
          error_instance_type: {},
        }


      },
      computed: {
        selected_polygon_key_has_nested_valued: function(){
          if(!this.diffgram_schema_mapping.polygon.points){
            return false
          }
          for(const elm in this.preLabels){
            const pointsValue = elm[this.diffgram_schema_mapping.polygon.points];
            if(typeof pointsValue === 'object' && pointsValue !== null){
              return true
            }
            else{
              return false;
            }
          }
          return false
        },
        instance_type_schema_is_set: function(){
          return this.diffgram_schema_mapping.instance_type != null;
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
                  $vm.preLabels = JSON.parse(textData);
                  const pre_label_keys = $vm.extract_pre_label_key_list($vm.preLabels);
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
        close: function(){
          this.is_open = false;
        },
        start_upload: function(){
          alert('start upload');
          this.close();
        },
        check_errors_and_go_to_step(step){
          console.log('stepppp', step, this.preLabels)
          if(step === 4){

            this.get_included_instance_types();
            if(!this.error_instance_type){
              this.el = step;
            }
          }

        },
        get_included_instance_types: function(){
          this.error_instance_type = {};
          for(const elm of this.preLabels){
            console.log('elm[this.diffgram_schema_mapping.instance_type]', elm[this.diffgram_schema_mapping.instance_type])
            if(elm[this.diffgram_schema_mapping.instance_type]){

              const instance_type = elm[this.diffgram_schema_mapping.instance_type];
              console.log('instance_type', instance_type)
              if(this.allowed_instance_types.includes(instance_type)){
                this.included_instance_types[instance_type] = true;
              }
              else{
                this.error_instance_type[instance_type] = `Invalid instance type "${instance_type}"`;
              }

            }
          }
        },
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

