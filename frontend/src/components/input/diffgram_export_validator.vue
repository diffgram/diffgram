<template>
  <v-container fluid :style="`position: relative; height: ${wizard_height}`">

    <div class="d-flex align-center">
      <v_error_multiple :error="errors_export_data" >
      </v_error_multiple>
      <v-alert dismissible type="success" v-if="success_missing_labels">Labels created successfully.</v-alert>
      <v-btn small
             v-if="errors_export_data && Object.keys(errors_export_data).length > 0 && !valid_labels && errors_export_data.label_names"
             color="secondary"
             @click="open_labels"><v-icon>mdi-brush</v-icon> Go To Labels
      </v-btn>
      <v-btn :loading="loading" class="ml-6" v-if="errors_export_data && Object.keys(errors_export_data).length > 0 && !valid_labels && errors_export_data.label_names" color="primary"
            small @click="create_missing_labels"><v-icon>mdi-plus</v-icon>Create Missing
      </v-btn>
    </div>

    <v-layout class="d-flex flex-column justify-center align-center pa-10">

      <v-container v-if="diffgram_export_ingestor" class="d-flex flex-column pa-0" style="height: 500px">
          <div key="0"
               v-if="current_question === 0"
               class="d-flex justify-center align-center">
            <div class="d-flex flex-column justify-start">

              <h1 class="secondary--text">
                <strong><v-icon color="secondary" large>mdi-test-tube</v-icon>Validating You Diffgram Export...</strong>
              </h1>
            </div>
          </div>
          <div class="d-flex justify-start mb-4">
            <h3 class="mr-6">1. Validating Export Metadata: </h3>
            <v-progress-circular indeterminate v-if="export_meta_data_state === 'loading'"></v-progress-circular>
            <v-icon v-else-if="export_meta_data_state === 'success'" color="success">mdi-check</v-icon>
            <v-icon v-else-if="export_meta_data_state === 'error'" color="error0">mdi-alert-circle</v-icon>
          </div>
        <div class="d-flex justify-start mb-4">
          <h3 class="mr-6">2. Validating File Names & Blobs: </h3>
          <v-progress-circular indeterminate v-if="file_names_state === 'loading'"></v-progress-circular>
          <v-icon v-else-if="file_names_state === 'success'" color="success">mdi-check</v-icon>
          <v-icon v-else-if="file_names_state === 'error'" color="error">mdi-alert-circle</v-icon>
        </div>
        <div class="d-flex justify-start mb-4">
          <h3 class="mr-6">3. Validating Labels: </h3>
          <v-progress-circular indeterminate v-if="label_names_state === 'loading'"></v-progress-circular>
          <v-icon v-else-if="label_names_state === 'success'" color="success">mdi-check</v-icon>
          <v-icon v-else-if="label_names_state === 'error'" color="error">mdi-alert-circle</v-icon>
        </div>
        <div class="d-flex justify-start mb-4">
          <h3 class="mr-6">4. Validating Instances: </h3>
          <v-progress-circular indeterminate v-if="instances_data_state === 'loading'"></v-progress-circular>
          <v-icon v-else-if="instances_data_state === 'success'" color="success">mdi-check</v-icon>
          <v-icon v-else-if="instances_data_state === 'error'" color="error">mdi-alert-circle</v-icon>
        </div>
      </v-container>
    </v-layout>
    <v-layout class="d-flex justify-space-between">
      <v-btn x-large
             :loading="loading"
             :disabled="current_question === 1"
             class="primary lighten-4 ma-8"
             style="justify-self: start; position: absolute; left: 0; bottom: 0"
             @click="previous_step(current_question)">
        Back
      </v-btn>
      <v-btn x-large
             style="justify-self: end; position: absolute; right: 0; bottom: 0"
             :disabled="export_validated"
             :loading="loading"
             data-cy="continue_file_mapping"
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
  import _ from "lodash";
  import {HexToHSVA, HexToRGBA, HSVAtoHSLA, get_random_color} from '../../utils/colorUtils'


  export default Vue.extend({
      name: 'file_schema_mapper',
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
        'diffgram_export_ingestor': {
          default: null
        }
      },
      data() {
        return {
          allowed_instance_types: [
            'box',
            'polygon',
            'line',
            'point',
            'cuboid',
            'ellipse',
          ],
          current_question: 0,
          missing_labels: [],
          errors_export_data: undefined,
          validation_stages: ['export_metadata', 'file_names', 'label_names', 'instances_data'],
          current_validation: 'export_meta_data',
          export_meta_data_state: 'loading',
          file_names_state: 'pending',
          label_names_state: 'pending',
          instances_data_state: 'pending',
          export_validated: false,
          success_missing_labels: false,
          wizard_height: '800px',
          valid_labels: false,
          loading: false,
        }
      },
      computed: {
      },
      watch: {},
      mounted() {
        if(this.$props.diffgram_export_ingestor){
          this.current_validation = 'export_metadata';
          this.validate_export_metadata();
        }

      },
      created() {
        window.addEventListener("resize", this.resize_wizard);
      },
      destroyed() {
        window.removeEventListener("resize", this.resize_wizard);
      },
      beforeDestroy() {

      },
      methods: {
        validate_export_metadata: async function(){
          this.export_meta_data_state = 'loading'
          await new Promise(resolve => setTimeout(resolve, 1500));
          try{
            this.diffgram_export_ingestor.check_export_meta_data();
            this.export_meta_data_state = 'success'
            this.validate_file_names();
          }
          catch (error) {
            console.error(error);
            this.errors_export_data = {}
            this.export_meta_data_state = 'error';
            this.errors_export_data['meta_data'] = error.toString();
          }


        },
        resize_wizard: function () {
          this.wizard_height = `${ window.innerHeight - 130}px`
        },
        open_labels: function () {
          window.open(`/project/${this.$props.project_string_id}/labels`, '_blank');
        },
        validate_file_names: async function () {
          try{

            this.file_names_state = 'loading';
            await new Promise(resolve => setTimeout(resolve, 200));
            try{
              const file_name_list = this.diffgram_export_ingestor.get_file_names();
              const file_blob_list = this.diffgram_export_ingestor.get_blob_list();
              this.file_names_state = 'success'
              this.validate_label_names();
            }
            catch (error) {
              console.error(error);
              this.errors_export_data = {};
              this.file_names_state = 'error';
              this.errors_export_data['files_data'] = error.toString();
            }

          }
          catch (e) {
            console.error(e)
          }
          finally {
            this.load_file_names = false;
          }
          return false
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
        next_step: async function (current_number, validate_data = true) {

        },
        create_missing_labels: async function(){
          this.loading = true
          this.success_missing_labels = false
          this.error = {}
          if(!this.missing_labels){
            return
          }
          for(const label_name of this.missing_labels){
            const random_color_hex = get_random_color();
            const rgba = HexToRGBA(random_color_hex);
            const hsv = HexToHSVA(random_color_hex);
            const hsl = HSVAtoHSLA(random_color_hex);
            const color_obj ={
              rgba,
              hsv,
              hsl,
              hex: random_color_hex,
              a: 1
            }
            try {
              const response = await axios.post('/api/v1/project/' + this.$props.project_string_id +'/label/new',
                {
                  colour: color_obj,
                  name: label_name,
                  default_sequences_to_single_frame: false
                });
              this.new_label_name = null

              // only if success?
              this.$store.commit('init_label_refresh')
              this.$emit('label_created', response.data.label)

            } catch (error) {
              this.loading = false

              if (error) {
                if (error.response.status == 400) {
                  this.error = error.response.data.log.error
                }
              }
              return

            }
          }
          this.success_missing_labels = true;
          this.loading = false
          this.missing_labels = [];



        },

        validate_label_names: async function () {
          try {
            this.label_names_state = 'loading';
            this.valid_labels = false;
            const response = await axios.get(`/api/project/${this.project_string_id}/labels/refresh`, {});
            if (response.status === 200) {
              const labels = response.data.labels_out;
              const label_names = labels.map(elm => elm.label.name)
              this.missing_labels = [];
              // Shallow copy before mutating data. Since the pre_labels are frozen (no reactivity)
              const export_label_names_list = this.diffgram_export_ingestor.get_label_names();
              for (const label_name of export_label_names_list) {
                if (!label_names.includes(label_name)) {
                  this.errors_export_data = {}
                  this.label_names_state = 'error'
                  this.errors_export_data['label_names'] = `The label name "${label_name}" does not exist in the project. Please create it.`
                  this.valid_labels = false;
                  this.load_label_names = false;
                  if(!this.missing_labels.includes(label_name)){
                    this.missing_labels.push(label_name)
                  }
                }
              }
            }

          } catch (e) {
            console.error(e);
            this.errors_export_data = this.$route_api_errors(e);
            this.valid_labels = false;
            this.load_label_names = false;
            this.label_names_state = 'error'
          } finally {

          }
        },
        validate_frames: function () {
          if (this.file_list_to_upload.filter(f => this.supported_video_files.includes(f.type)).length === 0) {
            return true
          }
          for (const instance of this.$props.pre_labeled_data) {
            const file_name = _.get(instance, this.diffgram_schema_mapping.file_name);
            const related_file = this.file_list_to_upload.find(f => f.name === file_name);
            if (!related_file) {
              this.errors_export_data['file_name'] = `No file named: ${file_name}`;
              this.errors_export_data['wrong_data'] = JSON.stringify(instance);
              return false
            }
            if (this.supported_video_files.includes(related_file.type)) {
              let frame_number = _.get(instance, this.diffgram_schema_mapping.frame_number)
              if (frame_number == undefined) {
                this.errors_export_data = {}
                this.errors_export_data['frame_number'] = `Provide frame numbers.`
                this.errors_export_data['wrong_data'] = JSON.stringify(instance)
                return false
              }
            }
          }
          return true
        },
        validate_sequences() {
          if (this.file_list_to_upload.filter(f => this.supported_video_files.includes(f.type)).length === 0) {
            return true
          }
          for (const instance of this.$props.pre_labeled_data) {
            const file_name = _.get(instance, this.diffgram_schema_mapping.file_name);
            const related_file = this.file_list_to_upload.find(f => f.name === file_name);
            if (!related_file) {
              this.errors_export_data['file_name'] = `No file named: ${file_name}`;
              this.errors_export_data['wrong_data'] = JSON.stringify(instance);
              return false
            }
            if (this.supported_video_files.includes(related_file.type)) {
              const seq_number = _.get(instance, this.diffgram_schema_mapping.number);
              if (seq_number == undefined) {
                this.errors_export_data = {}
                this.errors_export_data['sequence_numbers'] = `Provide Sequence numbers.`
                this.errors_export_data['wrong_data'] = JSON.stringify(instance)
                return false
              }
            }
          }
          return true
        },
        get_included_instance_types: function () {
          this.errors_export_data = {};
          for (const key of Object.keys(this.included_instance_types)) {
            this.$props.included_instance_types[key] = false;
          }
          for (const elm of this.$props.pre_labeled_data) {
            const instance_type = _.get(elm, this.diffgram_schema_mapping.instance_type)
            if (instance_type) {
              if (this.allowed_instance_types.includes(instance_type)) {
                this.included_instance_types[instance_type] = true;
              } else {
                this.errors_export_data = {};
                this.errors_export_data[instance_type] = `Invalid instance type "${instance_type}"`;
                return false;
              }

            } else {
              this.errors_export_data = {};
              this.errors_export_data['instance_type_field'] = `The select field should not be empty.`;
              return false;
            }
          }
          return true
        },
      }
    }
  ) </script>

<style>

</style>
