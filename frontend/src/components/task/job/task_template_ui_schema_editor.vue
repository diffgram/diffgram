<template>
<div>
  <h1>UI Schema: </h1>
  <ui_schema_selector
    v-if="job"
    data-cy="ui-schema-selector"
    :project_string_id="project_string_id"
    :show_default_option="true"
    :current_ui_schema_prop="job.ui_schema"
    @change="on_change_schema">

  </ui_schema_selector>
  <v-progress-linear v-else indeterminate></v-progress-linear>
</div>
</template>

<script>
import axios from '@/services/customInstance';
import ui_schema_selector from '../../ui_schema/ui_schema_selector'
import {get_task_template_details, update_task_template} from '@/services/taskTemplateService'
export default {
  name: "task_template_ui_schema_editor",
  props: {
    project_string_id: {
      required: true
    },
    job_id:{
      required: true
    }
  },
  components:{
    ui_schema_selector
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
          text: 'UI Schema updated succesfully.',
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
