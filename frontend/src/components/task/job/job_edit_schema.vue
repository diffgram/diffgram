<template>
  <div>
    <v-progress-linear v-if="loading"></v-progress-linear>
    <v-container v-if="job" class="d-flex flex-column">

      <label_schema_selector
        :initial_schema="job.label_schema"
        :project_string_id="$store.state.project.current.project_string_id"
        @change="on_change_schema"
      ></label_schema_selector>

      <v_error_multiple :error="error"> </v_error_multiple>
      <v-btn large
             @click="update_job_schema"
             :loading="loading_update"
             class="ma-auto" color="primary" width="300"><v-icon class="mr-2">mdi-content-save-all-outline</v-icon>Save</v-btn>
    </v-container>
  </div>
</template>

<script>
import label_schema_selector from '../../label/label_schema_selector'
import {get_task_template_details, update_task_template} from "@/services/taskTemplateService";
export default {
  name: "job_edit_schema",
  props: {
    project_string_id: {
      required: true
    },
    job_id:{
      required: true
    }
  },
  components:{
    label_schema_selector
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
      this.job.label_schema = schema;
      this.job.label_schema_id = schema.id
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
          text: 'Schema updated succesfully.',
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
