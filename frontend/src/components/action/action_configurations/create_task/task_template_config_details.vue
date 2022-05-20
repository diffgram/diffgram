<template>
  <div class="mb-4">
    <h3 class="">Select Tasks or Create New: </h3>
    <div  class="d-flex align-center">

      <job_select v-model="job_selected"
                  v-if="!show_task_template_wizard"
                  ref="job_select"
                  class="mr-4"
                  label="Select Task Template to Create tasks On"
                  @change="on_change_job"
                  :select_this_id="action.config_data.task_template_id"
      >
      </job_select>

      <div class="d-flex align-center justify-center">

        <v-btn :loading="switch_loading"
               outlined
               small
               v-if="!show_task_template_wizard"
               color="success" @click="show_wizard">
          <v-icon>mdi-plus</v-icon>
          Create New
        </v-btn>
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
  </div>
</template>

<script>
import task_template_wizard from '../../../task/job/task_template_wizard_creation/task_template_wizard'
import {create_empty_job} from '../../../task/job/empty_job'
import {Action} from './../../Action'
import Job_detail from "@/components/task/job/job_detail";
import Action_config_wizard_base from "@/components/action/actions_config_base/action_config_wizard_base";
export default {
  name: "task_template_config_details",
  props:{
    action:{
      required: true,
      type: Action
    },
    project_string_id: {
      required: true
    },
    actions_list: {
      required: true
    },
    display_mode:{
      default: "wizard"
    }
  },
  data: function(){
    return{
      job_to_create: create_empty_job(),
      job_selected: null,
      show_task_template_wizard: false,
      switch_loading: false,

    }
  },
  components: {
    Action_config_wizard_base,
    Job_detail,
    task_template_wizard: task_template_wizard,
  },
  methods: {
    on_launch: function(job){
      this.job_selected = job;
      this.$refs.job_select.add_job_to_list(job)
      this.$refs.job_select.select_job(job)
      this.action.config_data.task_template_id = job.id;
      this.$emit('action_updated', this.action)

    },
    on_change_job: function(job){
      this.action.config_data.task_template_id = job.id;
      this.$emit('action_updated', this.action)
    },
    hide_wizard: function(){
      this.show_task_template_wizard = false;
      this.job_to_create = null;
    },
    show_wizard: async function(){
      this.switch_loading = true;
      await this.$nextTick()
      this.show_task_template_wizard = true;
      await this.$nextTick()
      this.job_to_create = create_empty_job()
      this.switch_loading = false
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
