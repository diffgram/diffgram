<template>
  <v-container fluid :style="`position: relative; height: ${wizard_height}`">

    <div class="d-flex align-center">
      <v_error_multiple :error="errors_file_schema">
      </v_error_multiple>
      <v-alert dismissible type="success" v-if="success_missing_labels">Labels created successfully.</v-alert>
      <v-btn small v-if="errors_file_schema && Object.keys(errors_file_schema).length > 0 && !valid_labels && errors_file_schema.label_names" color="secondary"
             @click="open_labels"><v-icon>mdi-brush</v-icon> Go To Labels
      </v-btn>
      <v-btn :loading="loading" class="ml-6" v-if="errors_file_schema && Object.keys(errors_file_schema).length > 0 && !valid_labels && errors_file_schema.label_names" color="primary"
            small @click="create_missing_labels"><v-icon>mdi-plus</v-icon>Create Missing
      </v-btn>
    </div>
    <div class="d-flex align-center justify-center" v-if="load_file_ids">
      <h1>Validating File ID's... <v-progress-circular indeterminate></v-progress-circular></h1>
    </div>
    <div class="d-flex align-center justify-center" v-if="load_label_names">
      <h1>Validating Labels... <v-progress-circular indeterminate></v-progress-circular></h1>
    </div>

    <v-layout class="d-flex flex-column justify-center align-center pa-10">

      <v-container v-if="diffgram_schema_mapping" class="d-flex flex-column pa-0" style="height: 500px">

        <v-fade-transition> :group="true" hide-on-leave leave-absolute>

          <div key="0"
               v-if="current_question === 0"
               class="d-flex justify-center align-center">
            <div class="d-flex flex-column justify-start">

              <h1 class="secondary--text">
                <strong>
                  <v-icon large color="secondary">mdi-cable-data</v-icon>
                  Let's map your data!</strong>
              </h1>
              <p class="secondary--text">
                <strong>
                  The following questions will guide you towards the mapping of your JSON or CSV file to Diffgram's data
                  format:
                </strong>
              </p>

            </div>

          </div>
        </v-fade-transition>


        <v-fade-transition> :group="true" hide-on-leave leave-absolute>
          <div key="1" v-if="current_question === 1" class="d-flex justify-center align-center">
            <div class="d-flex flex-column justify-start">
              <h1 class="pa-2 black--text">Type:</h1>
              <h2> {{current_question}}) Select the Field Corresponding to the instance type.</h2>
              <h4>
                This field indicates what the instance type is (box, ellipse, polygon, etc). Please select
                the option on your file that corresponds to the instance type.
              </h4>
              <p style="font-size: 12px" class="primary--text text--lighten-3">
                <strong>
                  Allowed values here are:
                  {{allowed_instance_types}}
                </strong>
              </p>

              <v-container fluid class="d-flex justify-center flex-grow-1">

                <v-autocomplete
                  class="pt-4"
                  clearable
                  hide-selected
                  data-cy="select_instance_type"
                  :items="pre_label_key_list_filtered"
                  v-model="diffgram_schema_mapping.instance_type"
                >
                </v-autocomplete>

              </v-container>

            </div>

          </div>
        </v-fade-transition>

        <v-fade-transition> :group="true" hide-on-leave>
          <div key="2" v-if="current_question === 2" class="d-flex justify-start align-center">

            <div class="d-flex flex-column justify-start">
              <h1 class="pa-2 black--text">{{current_question}}) Label Name:</h1>
              <h4>
                This field indicates what the label name will be. For example if you are labeling cars,
                the it would contain something like "car".
              </h4>
              <p style="font-size: 12px" class="primary--text text--lighten-3">
                <strong>** Labels Must Already exist in project.</strong>
              </p>
              <v-container fluid class="d-flex justify-center flex-grow-1">
                <v-autocomplete
                  class="pt-4"
                  clearable
                  data-cy="select_label_name"
                  hide-selected
                  :items="pre_label_key_list_filtered"
                  menuProps="auto"
                  v-model="diffgram_schema_mapping.name">
                </v-autocomplete>
              </v-container>
            </div>
          </div>

        </v-fade-transition>
        <v-fade-transition> :group="true" hide-on-leave>
          <div key="3" v-if="current_question === 3 && upload_mode === 'new'" class="d-flex justify-start align-center">
            <div class="d-flex flex-column justify-start">
              <h1 class="pa-2 black--text">{{current_question}})File Name:</h1>
              <h4>
                This field indicates what the name of the file is (example: 'image1.jpg').
              </h4>
              <p style="font-size: 12px" class="primary--text text--lighten-3">
                <strong>** The value of this key must
                  match with the file name in order to identify the instances.
                </strong>
              </p>
              <v-container fluid class="d-flex justify-center flex-grow-1">
                <v-autocomplete class="pt-4"
                                clearable
                                data-cy="select_file_name"

                                hide-selected
                                :items="pre_label_key_list_filtered"
                                menuProps="auto"
                                v-model="diffgram_schema_mapping.file_name">
                </v-autocomplete>
              </v-container>
            </div>
          </div>
        </v-fade-transition>
        <v-fade-transition> :group="true" hide-on-leave>
          <div key="4" v-if="current_question === 3 && upload_mode === 'update'"
               class="d-flex justify-start align-center">
            <div class="d-flex flex-column justify-start">
              <h1 class="pa-2 black--text">{{current_question}}) Diffgram File ID:</h1>
              <h3 style="font-size: 12px" class="primary--text text--lighten-3"><strong>
                ** The value of this key must
                match with an existing Diffgram File ID.
              </strong>
              </h3>

              <v-container fluid class="d-flex justify-center flex-grow-1">
                <v-autocomplete class="pt-4"
                                clearable
                                data-cy="select_file_id"
                                menuProps="auto"
                                hide-selected
                                :items="pre_label_key_list_filtered"
                                v-model="diffgram_schema_mapping.file_id">
                </v-autocomplete>
              </v-container>
            </div>
          </div>
        </v-fade-transition>
        <v-fade-transition> :group="true" hide-on-leave>

          <div key="5" v-if="current_question === 4" class="d-flex justify-start align-center">
            <div class="d-flex flex-column justify-start">
              <h1 class="pa-2 black--text">{{current_question}}) Frame Number:</h1>
              <h3 style="font-size: 12px" class="primary--text text--lighten-3">
                <strong>
                  ** This field should indicate at what frame is this instance occuring. This value is a number
                  (Example: 3,5, 854, 15, etc)
                </strong>
              </h3>
              <v-container fluid class="d-flex justify-center flex-grow-1">
                <v-autocomplete class="pt-4"
                                clearable
                                menuProps="auto"
                                hide-selected
                                data-cy="select_frame_number"
                                :items="pre_label_key_list_filtered"
                                v-model="diffgram_schema_mapping.frame_number">">
                </v-autocomplete>
              </v-container>
            </div>
          </div>
        </v-fade-transition>
        <v-fade-transition> :group="true" hide-on-leave>
          <div key="6" v-if="current_question === 5" class="d-flex justify-start align-center">
            <div class="d-flex flex-column justify-start">
              <h1 class="pa-2 black--text">{{current_question}}) Sequence Number:</h1>
              <h3 style="font-size: 12px" class="primary--text text--lighten-3">
                <strong>
                  ** This field should indicate at what sequence this instance belongs to. This value is a number
                  (Example: 3,5, 854, 15, etc)
                </strong>
              </h3>
              <v-container fluid class="d-flex justify-center flex-grow-1">
                <v-autocomplete class="pt-4"
                                clearable
                                menuProps="auto"
                                hide-selected
                                data-cy="select_number"
                                :items="pre_label_key_list_filtered"
                                v-model="diffgram_schema_mapping.number">">
                </v-autocomplete>
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
                <v-btn x-large color="primary" data-cy="no_model_button" class="mr-8"
                       @click="next_step(current_question + 2, false)">
                  No
                </v-btn>
                <v-btn x-large color="primary" data-cy="use_model_button" @click="next_step(current_question)">
                  Yes
                </v-btn>
              </v-container>
            </div>
          </div>
        </v-fade-transition>
        <v-fade-transition> :group="true" hide-on-leave>
          <div key="7" v-if="current_question === 7" class="d-flex justify-start align-center">
            <div class="d-flex flex-column justify-start">
              <h1 class="pa-2 black--text">{{current_question}}) Model ID:</h1>
              <h3 style="font-size: 12px" class="primary--text text--lighten-3">
                <strong>
                  ** If model ID already exists, instances will be binded to existing the model.
                </strong>
              </h3>
              <v-container fluid class="d-flex justify-center flex-grow-1">
                <v-autocomplete class="pt-4"
                                menuProps="auto"
                                hide-selected
                                data-cy="select_model_id"

                                :items="pre_label_key_list_filtered"
                                v-model="diffgram_schema_mapping.model_id">
                </v-autocomplete>
              </v-container>
            </div>
          </div>
        </v-fade-transition>
        <v-fade-transition> :group="true" hide-on-leave>
          <div key="8" v-if="current_question === 8" class="d-flex justify-start align-center">
            <div class="d-flex flex-column justify-start">
              <h1 class="pa-2 black--text">{{current_question}}) Model Run ID:</h1>
              <h3 style="font-size: 12px" class="primary--text text--lighten-3">
                <strong>
                  ** If the Model Run ID already exists,
                  instances will be binded to the existing Model Run.
                </strong>
              </h3>
              <v-container fluid class="d-flex justify-center flex-grow-1">
                <v-autocomplete class="pt-4"
                                clearable
                                menuProps="auto"
                                hide-selected
                                data-cy="select_model_run_id"
                                :items="pre_label_key_list_filtered"
                                v-model="diffgram_schema_mapping.model_run_id">
                </v-autocomplete>
              </v-container>
            </div>
          </div>
        </v-fade-transition>
        <v-fade-transition> :group="true" hide-on-leave>
          <div key="9" v-if="current_question === 9" class="d-flex justify-start align-center">

            <div class="d-flex flex-column justify-start">
              <h1 class="pa-2 black--text">{{current_question}}) Do you want to add extra metadata to the file?</h1>
              <h4>
                You can attach a JSON object with special keys like sensor ID's or camera ID's to further identify
                and filter your dataset.
              </h4>
              <v-container fluid class="d-flex justify-center flex-grow-1 mt-8">
                <v-btn x-large color="primary" data-cy="no_metadata_button" class="mr-8" @click="next_step(current_question + 1, false)">
                  No
                </v-btn>
                <v-btn x-large color="primary" data-cy="yes_metadata_button" @click="next_step(current_question)">
                  Yes
                </v-btn>
              </v-container>
            </div>
          </div>
        </v-fade-transition>
        <v-fade-transition> :group="true" hide-on-leave>
          <div key="10" v-if="current_question === 10" class="d-flex justify-start align-center">
            <div class="d-flex flex-column justify-start">
              <h1 class="pa-2 black--text">{{current_question}}) File Metadata:</h1>
              <h3 style="font-size: 12px" class="primary--text text--lighten-3">
                <strong>
                  ** The metadata field must be a JSON object
                </strong>
              </h3>
              <v-container fluid class="d-flex justify-center flex-grow-1">
                <v-autocomplete class="pt-4"
                                clearable
                                data-cy="select_metadata"
                                menuProps="auto"
                                hide-selected
                                :items="pre_label_key_list_filtered"
                                v-model="diffgram_schema_mapping.file_metadata">
                </v-autocomplete>
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
             style="justify-self: start; position: absolute; left: 0; bottom: 0"
             @click="previous_step(current_question)">
        Back
      </v-btn>
      <v-btn x-large
             style="justify-self: end; position: absolute; right: 0; bottom: 0"
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
  import {HexToHSVA, HexToRGBA, HSVAtoHSLA} from '../../utils/colorUtils'


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
        'previously_completed_questions': {
          default: 0
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
          errors_file_schema: undefined,
          load_file_ids: false,
          success_missing_labels: false,
          wizard_height: '800px',
          load_label_names: false,
          loading: false,
          valid_labels: false,
        }
      },
      computed: {
        selected_keys: function () {
          const result = [];
          for (const key of Object.keys(this.diffgram_schema_mapping)) {
            const file_keys = ['instance_type', 'name', 'file_name', 'file_id', 'frame_number', 'number', 'model_id', 'model_run_id']
            if (this.diffgram_schema_mapping[key] && file_keys.includes(key)) {
              result.push(this.diffgram_schema_mapping[key])
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
        if(this.$refs.select_file_name){
          this.$refs.select_file_name.lastItem = 200;
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
        resize_wizard: function () {
          this.wizard_height = `${ window.innerHeight - 130}px`
        },
        open_labels: function () {
          window.open(`/project/${this.$props.project_string_id}/labels`, '_blank');
        },
        validate_file_names: function () {
          const file_name_list = [];
          for (const instance of this.$props.pre_labeled_data) {
            const file_name = _.get(instance, this.$props.diffgram_schema_mapping.file_name);
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
        previous_step: async function (current_number) {
          const old_number = parseInt(current_number, 10);
          this.current_question = undefined;
          await this.$nextTick();
          await new Promise(resolve => setTimeout(resolve, 500));
          await this.$nextTick();
          this.current_question = old_number - 1;
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
        validate_metadata: function(){
          for (const instance of this.$props.pre_labeled_data) {
            const metadata = _.get(instance, this.$props.diffgram_schema_mapping.file_metadata);
            if (typeof metadata !== 'object') {
              this.errors_file_schema = {};
              this.errors_file_schema[this.$props.diffgram_schema_mapping.file_name] = `File name should be a an object.`;
              this.errors_file_schema['wrong_data'] = metadata;
              return false
            } else {
              return true
            }
          }
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

          if (current_number == 0) {
            valid = true
          }

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
          } else if (current_number === 4) {
            // Validate frame numbers
            valid = this.validate_frames();
          } else if (current_number === 5) {
            // Validate frame sequences
            valid = this.validate_sequences();
          } else if (current_number === 6) {
            valid = true;
          } else if (current_number === 7) {
            valid = this.validate_model_id();
          } else if (current_number === 8) {
            valid = this.validate_mode_run_id();
          }
          else if(current_number === 9){
            valid = true
          }
          else if(current_number === 10 && validate_data){
            valid = this.validate_metadata();
          }

          else if(current_number === 10 && !validate_data){
            valid = true
          }

          if (valid) {
            if (current_number === 3) {
              // Check for the existence of Videos.
              if(this.upload_mode !== 'update'){
                const has_video = this.check_for_videos_in_uploaded_files();
                if (has_video) {
                  this.current_question = old_number + 1;
                  return
                } else {
                  this.current_question = old_number + 3;
                  return
                }
              }
              else{

                this.current_question = old_number + 3;
                return
              }

            }
            if (current_number === 10) {
              this.$emit('change_step_wizard')
              this.current_question = old_number;
              return
            }
            this.current_question = old_number + 1;
          } else {
            this.current_question = old_number;
          }
          this.$emit('complete_question', this.current_question + this.$props.previously_completed_questions)
          this.loading = false;
        },
        get_random_color: function(){
          const color = '#'+(Math.random()*0xFFFFFF<<0).toString(16);
          return color
        },
        create_missing_labels: async function(){
          this.loading = true
          this.success_missing_labels = false
          this.error = {}
          if(!this.missing_labels){
            return
          }
          for(const label_name of this.missing_labels){
            const random_color_hex = this.get_random_color();
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
            this.load_label_names = true
            this.valid_labels = false;
            const response = await axios.get(`/api/project/${this.project_string_id}/labels/refresh`, {});
            if (response.status === 200) {
              const labels = response.data.labels_out;
              const label_names = labels.map(elm => elm.label.name)
              this.missing_labels = [];
              // Shallow copy before mutating data. Since the pre_labels are frozen (no reactivity)
              const new_prelabeled_data = JSON.parse(JSON.stringify(this.$props.pre_labeled_data));
              for (const instance of new_prelabeled_data) {
                let label_name = _.get(instance, this.diffgram_schema_mapping.name)
                if (!label_names.includes(label_name)) {

                  this.errors_file_schema = {}
                  this.errors_file_schema['label_names'] = `The label name "${label_name}" does not exist in the project. Please create it.`
                  this.show_labels_link = false;
                  this.valid_labels = false;
                  this.load_label_names = false;
                  if(!this.missing_labels.includes(label_name)){
                    this.missing_labels.push(label_name)
                  }

                } else {
                  const label = labels.find(l => l.label.name === label_name);
                  instance.label_file_id = label.id;
                }
              }
              this.$emit('set_prelabeled_data', new_prelabeled_data)

              if(this.missing_labels.length > 0){
                this.load_label_names = false;
                return false
              }
              this.valid_labels = true;
              this.load_label_names = false;
              return true
            }

          } catch (e) {
            console.error(e);
            this.valid_labels = false;
            this.load_label_names = false;
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
              this.errors_file_schema['file_name'] = `No file named: ${file_name}`;
              this.errors_file_schema['wrong_data'] = JSON.stringify(instance);
              return false
            }
            if (this.supported_video_files.includes(related_file.type)) {
              let frame_number = _.get(instance, this.diffgram_schema_mapping.frame_number)
              if (frame_number == undefined) {
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
            const file_name = _.get(instance, this.diffgram_schema_mapping.file_name);
            const related_file = this.file_list_to_upload.find(f => f.name === file_name);
            if (!related_file) {
              this.errors_file_schema['file_name'] = `No file named: ${file_name}`;
              this.errors_file_schema['wrong_data'] = JSON.stringify(instance);
              return false
            }
            if (this.supported_video_files.includes(related_file.type)) {
              const seq_number = _.get(instance, this.diffgram_schema_mapping.number);
              if (seq_number == undefined) {
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
            const file_id_list = []
            const file_id_obj = {};
            this.load_file_ids = true;
            for(const inst of this.$props.pre_labeled_data){
              const file_id = _.get(inst, this.diffgram_schema_mapping.file_id);
              if(!file_id_obj[file_id]){
                file_id_list.push(file_id)
                file_id_obj[file_id] = true;
              }
            }
            for (const id of file_id_list) {
              if (isNaN(id)) {
                this.errors_file_schema['file_ids'] = 'File IDs must be numbers.'
                this.load_file_ids = false;
                return false;
              }
            }
            const response = await axios.post(`/api/v1/project/${this.$props.project_string_id}/file/exists`, {
              file_id_list: file_id_list
            });

            if (response.status === 200) {
              if (!response.data.exists) {
                this.load_file_ids = false;
                this.errors_file_schema['file_ids'] = 'Invalid file IDs on this JSON file. Please check that all files IDs exists on this project.'
                return false;
              } else {
                this.load_file_ids = false;
                return true
              }
            }
            return false
          } catch (error) {
            this.errors_file_schema = this.$route_api_errors(error)
            console.error(error)
            this.load_file_ids = false;
            return false;
          }
        },
        get_included_instance_types: function () {
          this.errors_file_schema = {};
          for (const key of Object.keys(this.included_instance_types)) {
            this.$props.included_instance_types[key] = false;
          }
          for (const elm of this.$props.pre_labeled_data) {
            const instance_type = _.get(elm, this.diffgram_schema_mapping.instance_type)
            if (instance_type) {
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
