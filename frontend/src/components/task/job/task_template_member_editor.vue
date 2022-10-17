<template>
<div v-if="job">
  <h1>Members:</h1>
  <member_select
    datacy="member-select"
    v-model="job.member_list_ids"
    label="Select Specific Users"
    :member_list="$store.state.project.current.member_list"
    :multiple="true"
    :initial_value="job.id != undefined ? job.member_list_ids : ['all']"
    :allow_all_option="true"
    :init_all_selected="false"
  >
  </member_select>
</div>
  <div v-else>
    <v-progress-circular size="250" v-model="loading"></v-progress-circular>
  </div>
</template>

<script>
import {get_task_template_details, update_task_template} from '@/services/taskTemplateService'
export default {
  name: "task_template_member_editor",
  props: {
    project_string_id: {
      required: true
    },
    job_id:{
      required: true
    }
  },
  components:{

  },
  data: function(){
    return {
      error: null,
      job: null,
      loading: false,
      loading_update: false
    }
  },
  mounted() {
    this.get_job_api();
  },
  methods:{
    on_change_schema: function(schema){
      this.job.ui_schema = schema;
      this.job.ui_schema_id = schema.id
      this.update_job_schema();
    },
    get_job_api: async function(){
      this.loading = true;
      let job = await get_task_template_details(this.job_id)
      if(job){
        this.job = job
      }
      this.loading = false;
    },
    update_job_schema: async function(){
      this.loading_update = true;
      let [result, error] = await update_task_template(this.project_string_id, this.job.id, this.job)
      if(error){
        console.error(error)
        this.error = this.$route_api_errors(error);
      }
      if(result){
        this.$store.commit('display_snackbar', {
          text: 'Members updated successfully.',
          color: 'success'
        })
      }
      this.loading_update = false;
    }
  }

}
</script>

<style scoped>

</style>
