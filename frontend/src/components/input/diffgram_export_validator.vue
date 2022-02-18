<template>
  <v-container fluid :style="`position: relative; height: ${wizard_height}`">

    <div class="d-flex align-center">

      <v_error_multiple :error="errors_export_data" >

      </v_error_multiple>
      <v-progress-circular indeterminate v-if="loading_attributes_creation || loading_labels_creation"></v-progress-circular>
      <v-alert dismissible type="success" v-if="success_missing_labels">Labels created successfully.</v-alert>
      <v-alert dismissible type="success" v-if="success_missing_attributes">Attributes created successfully.</v-alert>
      <v-btn small
             v-if="errors_export_data && Object.keys(errors_export_data).length > 0 && !valid_labels && errors_export_data.label_names"
             color="secondary"
             @click="open_labels"><v-icon>mdi-brush</v-icon> Go To Labels
      </v-btn>
      <v-btn :loading="loading_labels_creation" class="ml-6" v-if="errors_export_data && Object.keys(errors_export_data).length > 0 && !valid_labels && errors_export_data.label_names" color="primary"
            small @click="create_missing_labels"><v-icon>mdi-plus</v-icon>Create Missing Labels
      </v-btn>

      <v-btn small
             v-if="errors_export_data && Object.keys(errors_export_data).length > 0 && !valid_attributes && errors_export_data.attributes"
             color="secondary"
             @click="open_labels"><v-icon>mdi-brush</v-icon> Go To Attributes
      </v-btn>
      <v-btn :loading="loading_attributes_creation" class="ml-6" v-if="errors_export_data && Object.keys(errors_export_data).length > 0 && !valid_attributes && errors_export_data.attributes" color="primary"
             small @click="create_missing_attributes"><v-icon>mdi-plus</v-icon>Create Missing Attributes
      </v-btn>


    </div>
    <v-btn class="ml-5"
           @click="retry_all_checks"
           color="primary"
           small
           v-if="errors_export_data && Object.keys(errors_export_data).length > 0">
      <v-icon>mdi-refresh</v-icon>
      Recheck all Tests
    </v-btn>
    <v-layout class="d-flex flex-column justify-center align-center pa-10">

      <v-container v-if="diffgram_export_ingestor" class="d-flex flex-column pa-0" style="height: 500px">
          <div key="0"
               v-if="current_question === 0"
               class="d-flex justify-center align-center">
            <div class="d-flex flex-column justify-start">

              <h1 class="secondary--text">
                <strong><v-icon color="secondary" large>mdi-test-tube</v-icon>
                  Validating...
                </strong>
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
        <div class="d-flex justify-start mb-4">
          <h3 class="mr-6">5. Validating Attributes: </h3>
          <v-progress-circular indeterminate v-if="attributes_data_state === 'loading'"></v-progress-circular>
          <v-icon v-else-if="attributes_data_state === 'success'" color="success">mdi-check</v-icon>
          <v-icon v-else-if="attributes_data_state === 'error'" color="error">mdi-alert-circle</v-icon>
        </div>
      </v-container>
      <v-alert type="success" v-if="all_checks_passed" >All Checks Passed! Continue to next step. </v-alert>
    </v-layout>
    <v-layout class="d-flex justify-space-between">
      <v-btn x-large
             :loading="loading"
             :disabled="current_question === 1"
             class="primary lighten-4 ma-8"
             style="justify-self: start; position: absolute; left: 0; bottom: 0"
             @click="go_to_wizard_step(3)">
        Back
      </v-btn>
      <v-btn x-large
             style="justify-self: end; position: absolute; right: 0; bottom: 0"
             :disabled="!all_checks_passed"
             :loading="loading"
             data-cy="continue_file_mapping"
             class="primary ma-8"
             @click="go_to_wizard_step(6)">
        Continue
      </v-btn>
    </v-layout>
  </v-container>

</template>

<script lang="ts">
  import axios from '../../services/customAxiosInstance';
  import Vue from "vue";
  import _ from "lodash";
  import DiffgramExportFileIngestor from "./DiffgramExportFileIngestor";


  export default Vue.extend({
      name: 'diffgram_export_validator',
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
          type: DiffgramExportFileIngestor,
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
          validation_stages: ['export_metadata', 'file_names', 'label_names', 'instances_data', 'attributes_data'],
          current_validation: 'export_meta_data',
          export_meta_data_state: 'loading',
          file_names_state: 'pending',
          label_names_state: 'pending',
          instances_data_state: 'pending',
          attributes_data_state: 'pending',
          export_validated: false,
          success_missing_labels: false,
          missing_attributes: null,
          created_attribute_groups: null,
          existing_label_file_list: null,
          success_missing_attributes: false,
          wizard_height: '800px',
          valid_labels: false,
          existing_attribute_group_list: false,
          valid_attributes: false,
          loading_attributes_creation: false,
          loading: false,
          loading_labels_creation: false,
        }
      },
      computed: {
        all_checks_passed: function(){
          let state_keys = ['export_meta_data_state', 'file_names_state', 'label_names_state', 'instances_data_state', 'attributes_data_state'];
          for(let key of state_keys){
            if(this[key] != 'success'){
              return false
            }
          }
          return true;
        }
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
        go_to_wizard_step: function(num){
          this.$emit('go_to_wizard_step', num)
        },
        retry_all_checks: function(){
            this.file_names_state = 'pending';
            this.label_names_state = 'pending';
            this.instances_data_state = 'pending';
            this.export_meta_data_state = 'loading';
            this.attributes_data_state = 'pending';
            this.validate_export_metadata();
        },
        validate_export_metadata: async function(){
          this.export_meta_data_state = 'loading'
          this.errors_export_data = {};
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
        validate_instance_data: function(){
          this.instances_data_state = 'loading'
          try{

            this.diffgram_export_ingestor.validate_instances();

            this.instances_data_state = 'success'
            this.validate_attribute_groups();
          }
          catch (e) {
            console.error(e);
            this.errors_export_data = {};
            this.instances_data_state = 'error';
            this.errors_export_data['instance_validation'] = e.toString();
            this.errors_export_data['instance_validation'] = e.toString();
          }

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
        create_missing_labels: async function(){
          this.loading_labels_creation = true
          this.success_missing_labels = false
          this.error = {}
          this.errors_export_data = {}
          if(!this.missing_labels){
            return
          }
          for(const label_name of this.missing_labels){
            let label_file_id = this.diffgram_export_ingestor.get_label_file_id(label_name)
            let color = this.diffgram_export_ingestor.get_color_map(label_file_id)
            const color_obj = color
            try {
              const response = await axios.post('/api/v1/project/' + this.$props.project_string_id +'/label/new',
                {
                  colour: color_obj,
                  name: label_name,
                  default_sequences_to_single_frame: false
                });
              this.new_label_name = null

              // only if success?
              this.$store.commit('init_label_refresh');
              this.$emit('label_created', response.data.label);

            } catch (error) {
              this.loading_labels_creation = false

              if (error) {
                if (error.response.status == 400) {
                  this.error = error.response.data.log.error
                }
              }
              return

            }
          }
          this.success_missing_labels = true;
          this.loading_labels_creation = false
          this.missing_labels = [];
          this.retry_all_checks();


        },

        validate_label_names: async function () {
          try {
            this.label_names_state = 'loading';
            this.valid_labels = false;
            const response = await axios.get(`/api/project/${this.project_string_id}/labels/refresh`, {});
            if (response.status === 200) {
              const labels = response.data.labels_out;
              this.existing_label_file_list = labels;
              const label_map = {};
              for(let label of labels){
                label_map[label.label.name] = label.id;
              }
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
              if(this.missing_labels.length === 0){
                this.label_names_state = 'success';
                this.diffgram_export_ingestor.set_new_label_map(label_map)
                this.validate_instance_data()
              }
            }

          } catch (e) {
            console.error(e);
            this.errors_export_data = {};
            this.errors_export_data = this.$route_api_errors(e);
            this.errors_export_data['error'] = e.toString();
            this.valid_labels = false;
            this.load_label_names = false;
            this.label_names_state = 'error'
          } finally {

          }
        },
        fetch_attribute_group_list: async function(){
          try{
            const response = await axios.post(
              `/api/v1/project/${this.project_string_id}/attribute/template/list`,
              {
                group_id: this.attribute_template_group_id,
                with_labels: true,
                mode: 'from_project'

              });


            return  response.data.attribute_group_list;
          }
          catch (e) {
            console.error(e);
            this.errors_export_data = {};
            this.errors_export_data = this.$route_api_errors(e);
            this.instances_data_state = 'error'
          }
        },
        create_missing_attributes: async function(){
          if(!this.missing_attributes){
            return
          }
          try{
            this.created_attribute_groups = [];
            this.errors_export_data = {};
            this.success_missing_attributes = false;
            this.loading_attributes_creation = true;
            this.diffgram_export_ingestor.substitute_label_file_ids_on_attributes(this.existing_label_file_list)
            for(let attr_group of this.missing_attributes){
              const response = await axios.post(`/api/v1/project/${this.project_string_id}/attribute/group/new`,{})
              if(response.status === 200){
                let new_group = response.data.attribute_template_group;
                new_group.name = attr_group.name
                new_group.prompt = attr_group.prompt
                new_group.label_file_list = attr_group.label_file_list
                new_group.kind = attr_group.kind
                new_group.default_id = attr_group.default_id
                new_group.default_value = attr_group.default_value
                new_group.min_value = attr_group.min_value
                new_group.max_value = attr_group.max_value

                const response_update = await axios.post(`/api/v1/project/${this.project_string_id }/attribute/group/update`,
                  {
                    ...new_group,
                    group_id: new_group.id,
                    mode: 'UPDATE'
                  }
                )
                if(response_update.status === 200){
                  this.diffgram_export_ingestor.add_new_attr_id_mapping(attr_group.id, new_group.id);
                  if(attr_group.attribute_template_list){
                    new_group.attribute_template_list = []
                    for(const attribute of attr_group.attribute_template_list){
                      const response_attributes = await axios.post(`/api/v1/project/${this.project_string_id }/attribute`,
                        {
                          attribute:{
                            ...attribute,
                            id: null,
                            group_id: new_group.id
                          },
                          mode: 'NEW'
                        }
                      )
                      if(response_attributes.status === 200){
                        new_group.attribute_template_list.push(response_attributes.data.attribute_template)
                      }
                    }
                    this.diffgram_export_ingestor.map_attribute_options(attr_group, new_group);
                  }


                  this.created_attribute_groups.push(new_group)
                  this.$store.commit('attribute_refresh_group_list')

                }


              }
            }
            this.success_missing_attributes = true;
            this.retry_all_checks();
          }
          catch (e) {
            console.error(e);
            this.errors_export_data = {};
            this.errors_export_data['create_attribute'] = this.$route_api_errors(e)
            this.valid_attributes = false;

          }
          this.loading_attributes_creation = false;

        },
        validate_attribute_groups: async function(){
          try{
            this.attributes_data_state = 'loading'
            this.diffgram_export_ingestor.reset_attribute_mapping()
            this.existing_attribute_group_list = await this.fetch_attribute_group_list();
            let [has_missing_attributes, missing_attributes] = this.diffgram_export_ingestor.has_missing_attributes(this.existing_attribute_group_list);
            if(has_missing_attributes){
              this.errors_export_data = {};
              this.errors_export_data['attributes'] = `Missing Attributes: There are ${missing_attributes.length} missing attributes. Click create to create them automatically.`
              this.valid_attributes = false;
              this.missing_attributes = missing_attributes;
            }
            else{
              this.diffgram_export_ingestor.update_attribute_ids()
              this.attributes_data_state = 'success';
            }
          }
          catch (e) {
            console.error(e);
            this.errors_export_data = {};
            this.attributes_data_state = 'error'
            this.errors_export_data['attributes_validation'] = e.toString()
            this.valid_attributes = false;
          }
        }
      }
    }
  ) </script>

<style>

</style>
