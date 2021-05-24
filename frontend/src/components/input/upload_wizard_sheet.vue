<template>

  <v-bottom-sheet fullscreen v-if="is_open" v-model="is_open"
                  width="1700px" id="task-input-list-dialog"

            persistent>
    <v-layout style="position: relative; z-index: 999999">
      <v-btn class="" @click="close" icon x-large style="position: absolute; top: 0; right: -10px;">
        <v-icon>mdi-close</v-icon>
      </v-btn>
    </v-layout>

    <v-stepper v-model="el"  :non-linear="true" style="height: 100%;">

      <v-stepper-header class="ma-0 pl-8 pr-8">
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
          Match Instance Types to Diffgram Schema
        </v-stepper-step>
        <v-divider></v-divider>
        <v-stepper-step :complete="el > 4" step="4" editable>
          Confirm Upload
        </v-stepper-step>
      </v-stepper-header>

      <!-- Idea of this globally updating
        especially as large inner steps like mapping
        complete progress-->
      <v-progress-linear
        color="secondary"
        striped
        value="50"
        height="12"
      >
      </v-progress-linear>

      <v-stepper-items style="height: 100%">
        <v-stepper-content step="1" style="height: 100%">

          <new_or_update_upload_screen
            @upload_mode_change="upload_mode = $event"
            @file_update_error="file_update_error = $event"
            @file_list_updated="file_list_updated"
            @update_progress_percentage="update_progress_percentage"
            @error_upload_connections="error_upload_connections"
            @error_update_files="error_update_files = $event"
            @upload_in_progress="show_upload_progress_screen"
            @change_step_no_annotations="el = 4"
            @change_step_annotations="load_annotations_file"
            @progress_updated="update_progress_values"
            @reset_total_files_size="reset_total_files_size"
            @current_directory="set_current_directory"
            @file_added="file_added"
            ref="new_or_update_upload_screen"
            :initial_dataset="initial_dataset"
            :batch="batch"
            :error_file_uploads="error_file_uploads"
            :project_string_id="project_string_id">

          </new_or_update_upload_screen>

        </v-stepper-content>

        <v-stepper-content step="2">
          <file_schema_mapper
            :project_string_id="project_string_id"
            :pre_label_key_list="pre_label_key_list"
            :upload_mode="upload_mode"
            :included_instance_types="included_instance_types"
            :supported_video_files="supported_video_files"
            :diffgram_schema_mapping="diffgram_schema_mapping"
            :file_list_to_upload="file_list_to_upload"
            :pre_labeled_data="pre_labeled_data"
            @change_step_wizard="check_errors_and_go_to_step(3)"
            @set_included_instance_types="included_instance_types = $event"
          ></file_schema_mapper>
        </v-stepper-content>

        <v-stepper-content step="3">
          <instance_schema_mapper
            :project_string_id="project_string_id"
            :pre_label_key_list="pre_label_key_list"
            :upload_mode="upload_mode"
            :included_instance_types="included_instance_types"
            :supported_video_files="supported_video_files"
            :diffgram_schema_mapping="diffgram_schema_mapping"
            :file_list_to_upload="file_list_to_upload"
            :pre_labeled_data="pre_labeled_data"
            @change_step_wizard="check_errors_and_go_to_step(4)"
            @set_included_instance_types="included_instance_types = $event"
          ></instance_schema_mapper>
        </v-stepper-content>

        <v-stepper-content step="4">
          <upload_summary
            style="height: 100%"
            v-if="!upload_in_progress && file_list_to_upload"
            :file_list="file_list_to_upload.filter(f => f.data_type === 'Raw Media')"
            :upload_mode="upload_mode"
            :project_string_id="project_string_id"
            :pre_labeled_data="pre_labeled_data"
            :current_directory="current_directory"
            :diffgram_schema_mapping="diffgram_schema_mapping"
            @upload_raw_media="upload_raw_media"
            @created_batch="set_batch"
          ></upload_summary>
          <v_error_multiple :error="file_update_error"></v_error_multiple>
          <upload_progress
            v-if="upload_in_progress"
            :total_bytes="dropzone_total_file_size"
            :uploaded_bytes="dropzone_uploaded_file_size"
            :currently_uploading="currently_uploading_bytes"
            :progress_percentage="progress_percentage"
            @close_wizard="close"
          >

          </upload_progress>

        </v-stepper-content>

      </v-stepper-items>

    </v-stepper>
  </v-bottom-sheet>
</template>

<script lang="ts">
  import input_view from './input_view'
  import new_or_update_upload_screen from './new_or_update_upload_screen'
  import file_schema_mapper from './file_schema_mapper'
  import instance_schema_mapper from './instance_schema_mapper'
  import upload_summary from './upload_summary'
  import upload_progress from './upload_progress'
  import axios from 'axios';
  import Vue from "vue";

  function get_initial_state() {
    const initial_state = {
      csv_separator: ',',
      uploaded_bytes: null,
      upload_mode: 'new',
      progress_percentage: null,
      error_update_files: undefined,
      batch: null,
      file_update_error: undefined,
      error_file_uploads: null,
      total_bytes: null,
      percent_uploaded: null,
      current_directory: null,
      supported_video_files: ['video/mp4', 'video/x-msvideo', 'video/quicktime', 'video/x-m4v'],
      supported_image_files: ['image/jpg', 'image/jpeg', 'image/png'],


      diffgram_schema_mapping: {
        instance_type: null,
        file_id: null,
        name: null,
        file_name: null,
        frame_number: null,
        number: null,
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
          points_y: null,
          points_x: null,
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
      dropzone_total_file_size: 0,
      dropzone_uploaded_file_size: 0,
      currently_uploading_bytes: 0,
      upload_in_progress: false,
      valid_labels: false,
      pre_labeled_data: null,
      file_list_to_upload: [],

      pre_labels_file_list: [],
      pre_label_key_list: [],

      pre_labels_file_type: null,

    };
    return initial_state;
  }

  export default Vue.extend({
      name: 'upload_wizard_sheet',
      components: {
        input_view,
        upload_summary,
        file_schema_mapper,
        instance_schema_mapper,
        new_or_update_upload_screen,
        upload_progress
      },
      props: {
        'project_string_id': {
          default: null
        },
        'initial_dataset': {
          default: undefined
        }

      },

      data() {
        return get_initial_state();
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
          if (this.upload_mode === 'new') {
            return this.diffgram_schema_mapping.file_name != null;
          } else {
            return this.diffgram_schema_mapping.file_id != null;
          }

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
        this.set_current_directory(this.$store.state.project.current_directory)
      },

      beforeDestroy() {

      },

      methods: {
        update_progress_percentage: function (percent) {
          this.progress_percentage = percent
        },
        set_batch: function (batch) {
          this.batch = batch;
        },
        error_upload_connections: function (error) {
          this.connection_upload_error = error;
        },

        set_current_directory: function (current_directory) {
          this.current_directory = current_directory;
        },
        reset_total_files_size: function () {
          this.dropzone_total_file_size = 0;
        },
        file_added: function (file) {
          if (file.size) {
            this.dropzone_total_file_size += file.size;
          }
        },
        update_progress_values: function (file, total_bytes, uploaded_bytes) {
          this.currently_uploading_bytes = uploaded_bytes; // write totalBytes to dropzoneCurrentUpload
          if (file.size <= uploaded_bytes) {
            this.currently_uploading_bytes = 0; // reset current upload bytes counter
            this.dropzone_uploaded_file_size += uploaded_bytes; // add finished file to total upload
          }
        },
        show_upload_progress_screen: function () {
          this.upload_in_progress = true;
        },
        upload_raw_media: async function (file_list) {
          this.$refs.new_or_update_upload_screen.upload_raw_media(file_list);
        },
        load_annotation_from_local: function (file, text_data) {

          if (file.type === 'application/json') {
            this.pre_labels_file_type = 'json';
            this.pre_labeled_data = JSON.parse(text_data);
            const pre_label_keys = this.extract_pre_label_key_list(this.pre_labeled_data);
            this.pre_label_key_list = [...pre_label_keys];
            this.pre_labels_file_list.push(file);
          } else if (file.type === 'text/csv') {
            this.pre_labels_file_type = 'csv';
            let lines = text_data.split("\n");
            const headers = lines.shift().split(this.csv_separator)
            if (lines[lines.length - 1] == [""]) {
              lines.pop();
            }
            this.pre_label_key_list = headers;
            this.pre_labels_file_list.push(file);
            this.pre_labeled_data = lines.map(line => {
              const row = line.split(this.csv_separator)

              let obj = {};
              headers.forEach((h, i) => obj[h] = row[i]);
              return obj;
            })
          } else {
            throw new Error('Invalid file type for loading annotations')
          }
        },
        load_annotations_from_connection: async function () {
          const connector_id = this.$refs.new_or_update_upload_screen.incoming_connection.id;
          const directory_id = this.$store.state.project.current_directory.directory_id;
          const file = this.file_list_to_upload.filter(f => f.data_type === 'Annotations')[0];
          try {
            const response = await axios.post(`/api/walrus/v1/connectors/${connector_id}/fetch-data`, {
              opts: {
                action_type: 'get_string_data',
                path: file.id,
                bucket_name: this.$refs.new_or_update_upload_screen.bucket_name,
              },
              project_string_id: this.$props.project_string_id
            });

            if (response.status === 200) {
              const text_data = response.data.data;
              this.load_annotation_from_local(file, text_data);
            }

          } catch (error) {
            this.connection_upload_error = this.$route_api_errors(error);
            this.$emit('error_upload_connections', this.connection_upload_error)
            console.error(error);
          }
        },
        load_annotations_file: async function () {
          const file = this.file_list_to_upload.filter(f => f.data_type === 'Annotations')[0];
          this.$refs.new_or_update_upload_screen.loading_annotations = true;
          try {
            if (file.source === 'local') {
              const text_data = await file.text();
              await this.load_annotation_from_local(file, text_data);
            } else if (file.source === 'connection') {
              await this.load_annotations_from_connection(file);
            } else {
              throw new Error('Invalid source type from file. Must be: "connection" or "local" ');
            }
            this.el = 2;
          } catch (error) {
            this.error_file_uploads = {}
            this.error_file_uploads['annotations_file'] = `Error on file ${file.name}: ${error.toString()}`;
            console.error(error);
          }
          this.$refs.new_or_update_upload_screen.loading_annotations = false;

        },
        file_list_updated: function (new_file_list) {
          this.file_list_to_upload = new_file_list;
        },
        close: function () {
          this.is_open = false;
          Object.assign(this.$data, get_initial_state());
          this.$emit('closed')
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

        build_points_for_polygon() {
          if (this.pre_labels_file_type === 'json') {
            return
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
              return
            }
            if (x_points.length !== y_points.length) {
              this.errors_instance_schema = {};
              this.errors_instance_schema['x_points'] = 'X and Y values must be the same length';
              this.errors_instance_schema['wrong_data'] = JSON.stringify(instance);
              return
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
        },

        async check_errors_and_go_to_step(step) {
          console.log('check_errors_and_go_to_step', step)
          if (step === 3) {
            this.errors_file_schema = undefined;
            this.el = step;
          } else if (step === 4) {
            this.errors_instance_schema = undefined;
            this.build_points_for_polygon()
            if (this.errors_instance_schema) {
              return
            }
            for (const instance_key in this.included_instance_types) {
              if (this.included_instance_types[instance_key]) {
                for (const schema_key in this.diffgram_schema_mapping[instance_key]) {
                  if (!this.diffgram_schema_mapping[instance_key][schema_key]
                    && instance_key === 'polygon'
                    && ['points_x', 'points_y'].includes(schema_key)
                    && this.$props.pre_labels_file_type === 'json') {
                    // Skip polygon x,y points when pre_labels are in json format.
                    continue
                  }
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

<style>
  .v-stepper__wrapper{
    height: 100%;
  }
</style>
