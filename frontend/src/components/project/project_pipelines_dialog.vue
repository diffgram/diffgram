<template>
  <v-dialog v-model="is_open" max-width="1000px" id="export-dialog">
    <v-card>
        <v-card-title>
          Project Pipelines
        </v-card-title>

        <v-card-subtitle>
          This are the current data pipelines on your project:
        </v-card-subtitle>
        <v-card-text>
          <project_pipeline :initial_job_list="job_list"></project_pipeline>
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
  import project_pipeline from '../project/project_pipeline'
  export default Vue.extend(
    {
      components:{
        project_pipeline
      },
      props: {
        'project_string_id':{
          default: null
        },
        'job_list': {
          default: null
        }
      },
      name: "project_pipelines_dialog",
      computed:{},
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
