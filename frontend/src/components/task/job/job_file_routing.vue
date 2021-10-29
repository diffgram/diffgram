<template>
  <v-container class="ma-0" data-cy="job-file-routing">
    <v-row>
      <v-col cols="12">

        <v-card-title>
            1. Choose Diffgram Datasets for Tasks

            <button_with_menu
              tooltip_message="Streaming Info"
              icon="mdi-sync-circle"
              color="primary"
              :close_by_button="true"
                  >
              <template slot="content">
                <v-layout column>

                  <v-alert
                    text
                    type="info"
                  >
                    As files stream into datasets tasks will automatically be created. <br>
                    If a dataset already has files, at launch tasks will be created for all the existing files.
                    <a href="https://diffgram.readme.io/docs/job-directory-syncing"
                       target="_blank">Learn more</a>
                  </v-alert>

                </v-layout>
              </template>

          </button_with_menu>
        </v-card-title>

        <directory_icon_selector
          data-cy="directory-selector"
          layout_type="small"
          :job="job"
          :project_string_id="project_string_id"
          :attached_directories_list="attached_dirs"
          @directories-updated="on_directories_updated"
        ></directory_icon_selector>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12">
        <v-card-title>
          2. After Tasks are Completed (Optional)
        </v-card-title>

        <job_output_dir_selector
          data-cy="job-output-dir-selector"
          :job="job"
          :project_string_id="project_string_id"
          @output_dir_actions_update="on_output_dir_actions_update">
        </job_output_dir_selector>
      </v-col>
    </v-row>
  </v-container>

</template>

<script lang="ts">

  import axios from 'axios';
  import label_select_only from '../../label/label_select_only.vue'
  import upload_wizard_sheet from '../../input/upload_wizard_sheet'
  import directory_icon_selector from '../../source_control/directory_icon_selector.vue'
  import job_output_dir_selector from './job_output_dir_selector.vue'
  import {route_errors} from '../../regular/regular_error_handling'
  import Vue from "vue";


  export default Vue.extend({
      name: 'job_file_routing',
      model: {
        prop: 'job',
        event: 'change'
      },
      components: {
        label_select_only: label_select_only,
        directory_icon_selector: directory_icon_selector,
        job_output_dir_selector: job_output_dir_selector,
        upload_wizard_sheet: upload_wizard_sheet
      },
      props: {
        'job': {
          default: undefined,
          type: Object
        },
        'latest_dataset':{
          default: undefined,
          type: Object
        },
        'project_string_id': {
          default: undefined,
          type: String
        },
      },

      data() {
        return {
          attached_dirs: [],
          open_wizard: false,
          request_refresh: new Date()
        }
      },
      created() {
        this.update_attached_dirs();

      },
      watch: {
        job: function () {
          this.update_attached_dirs();
        }
      },
      methods: {
        on_close_wizard: function(){
          this.open_wizard = false;
          this.request_refresh = new Date();
        },
        open_import_data_sheet: async function(){
          this.open_wizard = true;
          await this.$nextTick();
          this.$refs.upload_wizard_sheet.open();
        },
        update_attached_dirs: function () {
          if (this.$props.job && this.$props.job.original_attached_directories_dict && this.$props.job.original_attached_directories_dict.attached_directories_list) {
            console.log('UPDATED DIRSSS',  this.$props.job.original_attached_directories_dict.attached_directories_list)
            this.attached_dirs = this.$props.job.original_attached_directories_dict.attached_directories_list;
          }
        },
        on_output_dir_actions_update: function(output_dir){
          this.$emit('output_dir_actions_update', output_dir)
        },
        on_directories_updated: function (dirs) {
          this.$emit('directories_updated', dirs)

        }
      }
    }
  ) </script>
