<template>
  <v-container fluid>
    <div class="d-flex align-center">
      <h2 class="font-weight-light mr-6">Select a Task Template: </h2>
      <job_select v-model="job_selected"
                  ref="job_select"
                  @change="on_change_job"
                  :select_this_id="action.job_id"
      >
      </job_select>
      <div class="d-flex justify-center ml-auto">
        <v-btn v-if="!show_task_template_wizard" color="success" @click="show_wizard"><v-icon>mdi-plus</v-icon>Create New Task Template</v-btn>
        <v-btn v-else outlined color="error" @click="hide_wizard"><v-icon>mdi-cancel</v-icon>Cancel Creation</v-btn>
      </div>
    </div>
    <div v-if="show_task_template_wizard">
      <task_template_wizard
        @task_template_launched="on_launch"
        :redirect_after_launch="false"
        :project_string_id="project_string_id"
        mode="new"
        :job="job_to_create"
      >
      </task_template_wizard>
    </div>
    <div v-else-if="action.job">
      <job_detail :job_id="action.job.id"></job_detail>
    </div>

  </v-container>
</template>

<script>
import directory_list from '../../source_control/directory_list'
import task_template_wizard from '../../task/job/task_template_wizard_creation/task_template_wizard'
import {create_empty_job} from '../../task/job/empty_job'
import Job_detail from "@/components/task/job/job_detail";
export default {
  name: "file_upload_action_config",
  props:{
    action:{
      required: true
    },
    project_string_id: {
      required: true
    }
  },
  data: function(){
    return{
      job_to_create: create_empty_job(),
      job_selected: null,
      show_task_template_wizard: false,

    }
  },
  components: {
    Job_detail,
    directory_list: directory_list,
    task_template_wizard: task_template_wizard,
  },
  methods: {
    on_launch: function(job){
      this.job_selected = job;
      this.$refs.job_select.add_job_to_list(job)
      this.$refs.job_select.select_job(job)
      this.action.job = job
      this.action.job_id = job.id

    },
    on_change_job: function(job){

    },
    hide_wizard: function(){
      this.show_task_template_wizard = false;
      this.job_to_create = null;
    },
    show_wizard: function(){
      this.show_task_template_wizard = true;
      this.job_to_create = create_empty_job()
    }
  },
  computed:{
    on_directories_updated: function(){

    }
  }
}
</script>

<style scoped>

</style>
