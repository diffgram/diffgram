<template>
  <v-container fluid>
    <v-tabs v-model="tab" class="mb-6" color="primary" style="height: 100%; border-bottom: 1px solid #e0e0e0">
      <v-tab v-for="item in items" :key="item.text">
        <v-icon left>{{ item.icon }}</v-icon>
        {{ item.text }}
      </v-tab>
    </v-tabs>
    <div class="d-flex flex-column">


      <div class="mb-4">
        <h2 class="font-weight-light mr-6">2. Add Condition [Optional]: </h2>
        <v-select   item-text="name" item-value="value" :items="conditions_list" v-model="action.condition_data.condition"></v-select>
      </div>


      <div class="mb-4">
        <h2 class="font-weight-light">3. Select Task Template or Create New: </h2>
        <div  class="d-flex align-center">
          <job_select v-model="job_selected"
                      v-if="!show_task_template_wizard"
                      ref="job_select"
                      class="mr-4"
                      label="Select Task Template to Create tasks On"
                      @change="on_change_job"
                      :select_this_id="action.job_id"
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

      <div class="mb-4">
        <h2 class="font-weight-light mr-6">4. Completes When: </h2>
        <v-select item-text="name" item-value="value" :items="completion_condition_list" v-model="action.complete_condition"></v-select>
      </div>

    </div>


  </v-container>
</template>

<script>
import directory_list from '../../source_control/directory_list'
import task_template_wizard from '../../task/job/task_template_wizard_creation/task_template_wizard'
import {create_empty_job} from '../../task/job/empty_job'
import {Action} from './../Action'
import Job_detail from "@/components/task/job/job_detail";
export default {
  name: "file_upload_action_config",
  props:{
    action:{
      required: true,
      type: Action
    },
    project_string_id: {
      required: true
    }
  },
  data: function(){
    return{
      tab: 0,
      items: [
        { text: "Details", icon: "mdi-view-dashboard" },
        { text: "Step Configuration", icon: "mdi-cog" },
      ],

      completion_condition_list: [
        {
          name: 'Task is Completed',
          value: 'task_completed'
        }
      ],
      conditions_list: [
        {
          name: 'Image Files Only',
          value: 'images_only'
        },
        {
          name: 'Video Files Only',
          value: 'videos_only'
        },
        {
          name: 'Text Files Only',
          value: 'text_only'
        },
        {
          name: '3D Files Only',
          value: '3d_only'
        },
        {
          name: 'Geospatial Files Only',
          value: 'geo_only'
        }
      ],
      job_to_create: create_empty_job(),
      job_selected: null,
      show_task_template_wizard: false,
      switch_loading: false,

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
