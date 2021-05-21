<template>
  <v-container fluid>
    <v_error_multiple :error="errors_file_schema">
    </v_error_multiple>
    <v-layout class="d-flex flex-column justify-center align-center pa-10">
      <h1 class="secondary--text">
        <strong>
          <v-icon large color="secondary">mdi-cable-data</v-icon>
          Let's map your data!</strong>
      </h1>
      <p class="secondary--text">
        <strong>
          The following questions will guide you towards the mapping of your JSON or CSV file to Diffgram's data format:
        </strong>
      </p>
      <v-container v-if="diffgram_schema_mapping" class="d-flex flex-column pa-0" style="height: 500px">
        <v-fade-transition> :group="true" hide-on-leave leave-absolute>
          <div key="1" v-if="current_question === 1" class="d-flex justify-center align-center">
            <div class="d-flex flex-column justify-start">
              <h1 class="pa-2 black--text">{{current_question}}) Select the Field Corresponding to the instance
                type:</h1>
              <h4>
                This field indicates what the instance type is (box, ellipse, polygon, etc). Please select
                the option on your file that corresponds to the instance type.
              </h4>
              <p style="font-size: 12px" class="primary--text text--lighten-3">
                <strong>
                  ** Allowed values here are:
                  {{allowed_instance_types}}
                </strong>
              </p>
              <v-container fluid class="d-flex justify-center flex-grow-1">
                <v-select class="pt-4"
                          clearable
                          :items="pre_label_key_list"
                          v-model="diffgram_schema_mapping.instance_type">
                </v-select>
              </v-container>
            </div>

          </div>
        </v-fade-transition>
        <v-fade-transition> :group="true" hide-on-leave>
          <div key="2" v-if="current_question === 2" class="d-flex justify-start align-center">

            <div class="d-flex flex-column justify-start">
              <h1 class="pa-2 black--text">{{current_question}}) Select the Field Corresponding to the Label Name:</h1>
              <h4>
                This field indicates what the label name will be. For example if you are labeling cars,
                the it would contain something like "car".
              </h4>
              <p style="font-size: 12px" class="primary--text text--lighten-3">
                <strong>** Labels Must Already exist in project.</strong>
              </p>
              <v-container fluid class="d-flex justify-center flex-grow-1">
                <v-select class="pt-4"
                          clearable
                          :items="pre_label_key_list"
                          v-model="diffgram_schema_mapping.name">
                </v-select>
              </v-container>
            </div>
          </div>

        </v-fade-transition>
        <v-fade-transition> :group="true" hide-on-leave>
          <div key="3" v-if="current_question === 3 && upload_mode === 'new'" class="d-flex justify-start align-center">
            <div class="d-flex flex-column justify-start">
              <h1 class="pa-2 black--text">{{current_question}}) Select the Field Corresponding to the File Name:</h1>
              <h4>
                This field indicates what the name of the file is (example: 'image1.jpg').
              </h4>
              <p style="font-size: 12px" class="primary--text text--lighten-3">
                <strong>** The value of this key must
                  match with the file name in order to identify the instances.
                </strong>
              </p>
              <v-container fluid class="d-flex justify-center flex-grow-1">
                <v-select class="pt-4"
                          clearable
                          :items="pre_label_key_list"
                          v-model="diffgram_schema_mapping.file_name">
                </v-select>
              </v-container>
            </div>
          </div>
        </v-fade-transition>
        <v-fade-transition> :group="true" hide-on-leave>
          <div key="4" v-if="current_question === 3 && upload_mode === 'update'"
               class="d-flex justify-start align-center">
            <div class="d-flex flex-column justify-start">
              <h1 class="pa-2 black--text">{{current_question}}) Select the Field Corresponding to the Diffgram File ID:</h1>
              <h3 style="font-size: 12px" class="primary--text text--lighten-3"><strong>
                ** The value of this key must
                match with an existing Diffgram File ID.
              </strong>
              </h3>

              <v-container fluid class="d-flex justify-center flex-grow-1">
                <v-select class="pt-4"
                          clearable
                          :items="pre_label_key_list"
                          v-model="diffgram_schema_mapping.file_id">
                </v-select>
              </v-container>
            </div>
          </div>
        </v-fade-transition>
        <v-fade-transition> :group="true" hide-on-leave>

          <div key="5" v-if="current_question === 4" class="d-flex justify-start align-center">
            <div class="d-flex flex-column justify-start">
              <h1 class="pa-2 black--text">{{current_question}}) Select the Field Corresponding to the frame number:</h1>
              <h3 style="font-size: 12px" class="primary--text text--lighten-3">
                <strong>
                  ** This field should indicate at what frame is this instance occuring. This value is a number
                  (Example: 3,5, 854, 15, etc)
                </strong>
              </h3>
              <v-container fluid class="d-flex justify-center flex-grow-1">
                <v-select class="pt-4"
                          clearable
                          :items="pre_label_key_list"
                          v-model="diffgram_schema_mapping.frame_number">">
                </v-select>
              </v-container>
            </div>
          </div>
        </v-fade-transition>
        <v-fade-transition> :group="true" hide-on-leave>
          <div key="6" v-if="current_question === 5" class="d-flex justify-start align-center">
            <div class="d-flex flex-column justify-start">
              <h1 class="pa-2 black--text">{{current_question}}) Select the Field Corresponding to the Sequence Number:</h1>
              <h3 style="font-size: 12px" class="primary--text text--lighten-3">
                <strong>
                  ** This field should indicate at what sequence this instance belongs to. This value is a number
                  (Example: 3,5, 854, 15, etc)
                </strong>
              </h3>
              <v-container fluid class="d-flex justify-center flex-grow-1">
                <v-select class="pt-4"
                          clearable
                          :items="pre_label_key_list"
                          v-model="diffgram_schema_mapping.number">">
                </v-select>
              </v-container>
            </div>
          </div>
        </v-fade-transition>
        <v-fade-transition> :group="true" hide-on-leave>
          <div key="7" v-if="current_question === 6" class="d-flex justify-start align-center">

            <div class="d-flex flex-column justify-start">
              <h1 class="pa-2 black--text">{{current_question}}) Do you want to Map your Model's ID to the data?</h1>
              <h4>
                You can attach a Model ID and a Model Run ID from your system to identify which model generated the
                instances. This is an optional step.
              </h4>
              <v-container fluid class="d-flex justify-center flex-grow-1 mt-8">
                <v-btn x-large color="primary" class="mr-8" @click="next_step(current_question + 2, false)">
                  No
                </v-btn>
                <v-btn x-large color="primary" @click="next_step(current_question)">
                  Yes
                </v-btn>
              </v-container>
            </div>
          </div>
        </v-fade-transition>
        <v-fade-transition> :group="true" hide-on-leave>
          <div key="7" v-if="current_question === 7" class="d-flex justify-start align-center">
            <div class="d-flex flex-column justify-start">
              <h1 class="pa-2 black--text">{{current_question}}) Select the Field Corresponding to the Model ID:</h1>
              <h3 style="font-size: 12px" class="primary--text text--lighten-3">
                <strong>
                  ** If model ID already exists, instances will be binded to existing the model.
                </strong>
              </h3>
              <v-container fluid class="d-flex justify-center flex-grow-1">
                <v-select class="pt-4"
                          clearable
                          :items="pre_label_key_list"
                          v-model="diffgram_schema_mapping.model_id">
                </v-select>
              </v-container>
            </div>
          </div>
        </v-fade-transition>
        <v-fade-transition> :group="true" hide-on-leave>
          <div key="8" v-if="current_question === 8" class="d-flex justify-start align-center">
            <div class="d-flex flex-column justify-start">
              <h1 class="pa-2 black--text">{{current_question}})Select the Field Corresponding to the Model Run ID:</h1>
              <h3 style="font-size: 12px" class="primary--text text--lighten-3">
                <strong>
                  ** If the Model Run ID already exists,
                  instances will be binded to the existing Model Run.
                </strong>
              </h3>
              <v-container fluid class="d-flex justify-center flex-grow-1">
                <v-select class="pt-4"
                          clearable
                          :items="pre_label_key_list"
                          v-model="diffgram_schema_mapping.model_run_id">
                </v-select>
              </v-container>
            </div>
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
      name: 'file_schema_mapper',
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
          allowed_instance_types: [
            'box',
            'polygon',
            'line',
            'point',
            'cuboid',
            'ellipse',
          ],
          current_question: 1,
          valid_value: {},
          errors_file_schema: undefined,
          load_label_names: false,
          loading: false,
          valid_value: false,
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
        validate_file_names: function () {
          const file_name_list = [];
          for (const instance of this.$props.pre_labeled_data) {
            const file_name = instance[this.$props.diffgram_schema_mapping.file_name];
            if (typeof file_name === 'number') {
              this.errors_file_schema = {};
              this.errors_file_schema[this.$props.diffgram_schema_mapping.file_name] = `File name should be a string not a number.`;
              this.errors_file_schema['wrong_data'] = file_name;
              return false
            } else {
              if (!file_name_list.includes(file_name)) {
                file_name_list.push(file_name)
              }
            }
          }
          const file_names_to_upload = this.$props.file_list_to_upload.map(f => f.name);
          for (const file_name of file_name_list) {
            if (!file_names_to_upload.includes(file_name)) {
              this.errors_file_schema = {};
              this.errors_file_schema['file_name'] = `File ${file_name} does not exists in the uploaded data.
               Please make sure to upload the file name: ${file_name}`;
              this.errors_file_schema['wrong_data'] = file_name;
              return false
            }
          }

          return true;
        },
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
        next_step: async function (current_number, validate_data = true) {
          let valid = false;
          let loading = true;
          const old_number = parseInt(current_number, 10);
          this.current_question = undefined;
          await this.$nextTick();
          await new Promise(resolve => setTimeout(resolve, 500));
          await this.$nextTick();
          this.errors_file_schema = undefined;

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
        validate_label_names: async function () {
          try {
            this.load_label_names = true
            this.valid_labels = false;
            const response = await axios.get(`/api/project/${this.project_string_id}/labels/refresh`, {});
            if (response.status === 200) {
              const labels = response.data.labels_out;
              const label_names = labels.map(elm => elm.label.name)
              for (const instance of this.$props.pre_labeled_data) {
                if (!label_names.includes(instance[this.diffgram_schema_mapping.name])) {
                  this.errors_file_schema = {}
                  this.errors_file_schema['label_names'] = `The label name "${instance[this.diffgram_schema_mapping.name]}" does not exist in the project. Please create it.`
                  this.valid_labels = false;
                  this.load_label_names = false;
                  return false
                } else {
                  const label = labels.find(l => l.label.name === instance[this.diffgram_schema_mapping.name]);
                  instance.label_file_id = label.id;
                }
              }
              this.valid_labels = true;
              return true
            }

          } catch (e) {
            console.error(e);
            this.valid_labels = false;
            this.load_label_names = false;
          } finally {

          }
        },
        validate_frames: function(){
          if (this.file_list_to_upload.filter(f => this.supported_video_files.includes(f.type)).length === 0) {
            return true
          }
          for (const instance of this.$props.pre_labeled_data) {
            const related_file = this.file_list_to_upload.find(f => f.name === instance[this.diffgram_schema_mapping.file_name]);
            if (!related_file) {
              this.errors_file_schema['file_name'] = `No file named: ${instance[this.diffgram_schema_mapping.file_name]}`;
              this.errors_file_schema['wrong_data'] = JSON.stringify(instance);
              return false
            }
            if (this.supported_video_files.includes(related_file.type)) {
              if (instance[this.diffgram_schema_mapping.frame_number] == undefined) {
                this.errors_file_schema = {}
                this.errors_file_schema['frame_number'] = `Provide frame numbers.`
                this.errors_file_schema['wrong_data'] = JSON.stringify(instance)
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
            const related_file = this.file_list_to_upload.find(f => f.name === instance[this.diffgram_schema_mapping.file_name]);
            if (!related_file) {
              this.errors_file_schema['file_name'] = `No file named: ${instance[this.diffgram_schema_mapping.file_name]}`;
              this.errors_file_schema['wrong_data'] = JSON.stringify(instance);
              return false
            }
            if (this.supported_video_files.includes(related_file.type)) {
              if (instance[this.diffgram_schema_mapping.number] == undefined) {
                this.errors_file_schema = {}
                this.errors_file_schema['sequence_numbers'] = `Provide Sequence numbers.`
                this.errors_file_schema['wrong_data'] = JSON.stringify(instance)
                return false
              }
            }
          }
          return true
        },
        async validate_file_id_list_for_update() {
          try {
            if (this.upload_mode !== 'update') {
              return true
            }
            const file_id_list = this.$props.pre_labeled_data.map(inst => inst[this.diffgram_schema_mapping.file_id]);
            for (const id of file_id_list) {
              if (isNaN(id)) {
                this.errors_file_schema['file_ids'] = 'File IDs must be numbers.'
                return false;
              }
            }
            const response = await axios.post(`/api/v1/project/${this.$props.project_string_id}/file/exists`, {
              file_id_list: file_id_list
            });

            if (response.status === 200) {
              if (!response.data.exists) {
                this.errors_file_schema['file_ids'] = 'Invalid file IDs on this JSON file. Please check that all files IDs exists on this project.'
                return false;
              } else {
                return true
              }
            }
            return false
          } catch (error) {
            this.errors_file_schema = this.$route_api_errors(error)
            console.error(error)
            return false;
          }
        },
        get_included_instance_types: function () {
          this.errors_file_schema = {};
          for (const key of Object.keys(this.included_instance_types)) {
            this.$props.included_instance_types[key] = false;
          }
          for (const elm of this.$props.pre_labeled_data) {
            if (elm[this.diffgram_schema_mapping.instance_type]) {

              const instance_type = elm[this.diffgram_schema_mapping.instance_type];
              if (this.allowed_instance_types.includes(instance_type)) {
                this.included_instance_types[instance_type] = true;
              } else {
                this.errors_file_schema = {};
                this.errors_file_schema[instance_type] = `Invalid instance type "${instance_type}"`;
                return false;
              }

            } else {
              this.errors_file_schema = {};
              this.errors_file_schema['instance_type_field'] = `The select field should not be empty.`;
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
