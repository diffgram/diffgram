<template>
  <div>
    <v-progress-linear v-if="loading"></v-progress-linear>
    <v-container v-if="!loading && job" class="d-flex flex-column">
      <v-row class="d-flex pa-0 justify-space-between">
        <v-col cols="6" class="pa-0 ">
          <job_file_routing
            :job="job"
            style="border-right: 2px solid #e6e6e6"
            :latest_dataset="latest_dataset"
            :project_string_id="project_string_id"
            ref="job_file_routing"
            @directories_updated="on_attached_dirs_updated"
            @output_dir_actions_update="on_output_dirs_updated"
          ></job_file_routing>

        </v-col>
        <v-col class="pa-0 " cols="6">
          <job_pipeline_mxgraph  ref="job_pipeline" :job_object="job"></job_pipeline_mxgraph>
        </v-col>
      </v-row>
      <v-row class="d-flex justify-center align-center">
        <v-btn :disabled="!has_changed"large color="success" @click="on_save_button_click"><v-icon>mdi-save</v-icon>Save</v-btn>
      </v-row>

    </v-container>
  </div>
</template>

<script>
import axios from "../../../services/customInstance/index.js";
import label_schema_selector from '../../label/label_schema_selector'
import {get_task_template_details, update_task_template} from "@/services/taskTemplateService";
import job_pipeline_mxgraph from "@/components/task/job/job_pipeline_mxgraph.vue";
import job_file_routing from "@/components/task/job/job_file_routing.vue";
import _ from 'lodash';
export default {
  name: "job_edit_pipeline",
  props: {
    project_string_id: {
      required: true
    },
    job_id:{
      required: true
    }
  },
  components:{
    job_file_routing,
    job_pipeline_mxgraph,
    label_schema_selector
  },
  data: function(){
    return {
      error: null,
      job: null,
      output_dir: null,
      original_output_dir: null,
      original_output_dir_action: null,
      latest_dataset: undefined,
      loading: false,
      loading_update: false
    }
  },
  async mounted() {
    await this.get_job_api();
  },
  computed: {
    has_changed: function(){
      if(!this.output_dir){
        return
      }
      let has_changed = false
      if(!_.isEqual(this.job.attached_directories_dict, this.job.original_attached_directories_dict)){
        has_changed = true
        return has_changed
      }
      if(this.output_dir.action !== this.original_output_dir_action){
        has_changed = true
        return has_changed
      }
      let id = null;
      if(this.output_dir.directory && this.output_dir.directory.id != undefined){
        id = this.output_dir.directory.id
      }
      if(id !== this.original_output_dir){
        has_changed = true
        return has_changed
      }
      return false

    }
  },
  methods:{
    async add_output_actions_to_job() {
      this.loading = true
      this.show_success = false
      this.error_launch = {}
      if (this.output_dir.action === 'copy' || this.output_dir.action === 'move') {
        if (!this.output_dir.directory) {
          this.error_launch = {
            output_dir: 'Please select a directory for copy/move after tasks are completed.'
          }
          this.loading = false;
          return false
        }
      }
      try {
        const response = await axios.post(
          `/api/v1/project/${this.project_string_id}/job/set-output-dir`,
          {
            output_dir: this.output_dir.directory ? this.output_dir.directory.directory_id.toString() : undefined,
            output_dir_action: this.output_dir.action,
            job_id: parseInt(this.job.id),
          })
        return response
      } catch (error) {
        if (error.response) {
          this.error = error.response.data.log.error
        }
        this.loading = false
        return false
      }
    },
    async add_dirs_to_job_api() {
      this.loading = true
      this.show_success = false
      this.error_launch = {}
      let dir_list = [];
      if (this.job && this.job.attached_directories_dict && this.job.attached_directories_dict.attached_directories_list) {
        dir_list = this.job.attached_directories_dict.attached_directories_list
      }
      try {
        const response = await axios.post(
          '/api/v1/project/' + this.project_string_id
          + '/job/dir/attach',
          {
            directory_list: dir_list,
            job_id: parseInt(this.job.id),
          })
        return response
      } catch (error) {
        console.error(error)
        if (error.response) {
          this.error_launch = error.response.data.log.error
        }
        this.loading = false
        return false;
      }
    },
    on_save_button_click: async function(){
      this.error = {};
      let dirs_ok = await this.add_dirs_to_job_api();
      let out_dirs_ok = await this.add_output_actions_to_job();
      console.log('dirs_ok', dirs_ok)
      console.log('out_dirs_ok', out_dirs_ok)
      if(dirs_ok && out_dirs_ok){
        this.$store.commit('display_snackbar', {
          text: 'Pipeline updated successfully.',
          color: 'success'
        })
      }
      await this.get_job_api()
    },
    on_attached_dirs_updated: function(attached_dirs){
      console.log('ATTACHED DIRS')
      this.latest_dataset = attached_dirs[attached_dirs.length - 1];
      this.job.attached_directories_dict = {
        attached_directories_list: attached_dirs.map(elm => elm)
      }
      if(!this.$refs.job_pipeline){
        return
      }
      this.$refs.job_pipeline.redraw()
    },
    on_output_dirs_updated: async function(output_dir){
      console.log('output_dir DIRS', output_dir)
      this.output_dir = {...output_dir};
      if(!this.$refs.job_pipeline){
        return
      }
      this.$refs.job_pipeline.redraw()
    },
    get_job_api: async function(){
      this.loading = true;
      let job = await get_task_template_details(this.job_id)
      console.log('JOBS', job)
      job.original_attached_directories_dict = {
        ...job.attached_directories_dict,
      };
      this.original_output_dir_action = job.output_dir_action ? job.output_dir_action : 'nothing'
      this.original_output_dir = job.completion_directory_id

      if(job){
        this.job = job
      }

      this.loading = false;
      await this.$nextTick()
      this.$refs.job_pipeline.redraw()
    },
  }

}
</script>

<style scoped>

</style>
