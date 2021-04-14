<template>
  <v-dialog v-model="is_open" max-width="1000px" id="export-dialog">
    <v-card>
        <v-card-title>
          Task Template Pipeline
        </v-card-title>

        <v-card-subtitle>
          This is the data pipeline of your Task Template
        </v-card-subtitle>
        <v-card-text>
          <job_pipeline_mxgraph :job_object="job"
                                :show_output_jobs="true"
                                class="mt-4 mb-4 pb-8 pt-8">

          </job_pipeline_mxgraph>

        </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="blue darken-1" text @click="close">Close</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
  import Vue from "vue";
  import job_pipeline_mxgraph from '../job/job_pipeline_mxgraph'
  export default Vue.extend(
    {
      components:{
        job_pipeline_mxgraph
      },
      props: {
        'project_string_id':{
          default: null
        },
        'job': {
          default: null
        }
      },
      name: "job_pipelines_dialog",
      computed:{
        job_id: function(){
          if(this.$props.job){
            return this.$props.job.id;
          }
        }
      },
      data (){
        return {
          is_open: false
        }
      },
      methods: {
        open(){
          this.is_open = true;
        },
        close(){
          this.is_open = false
        }
      },
    }
  )
</script>

<style scoped>

</style>
