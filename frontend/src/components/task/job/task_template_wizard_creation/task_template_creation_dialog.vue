<template>
  <v-dialog v-if="is_open" v-model="is_open" max-width="1600px" class="d-flex flex-column align-center justify-center ma-auto"  id="export-dialog">
    <v-card fluid elevation="0" class="pa-4 pt-8">
      <v-card-text v-if="!loading">
        <task_template_wizard

          :project_string_id="project_string_id"
          mode="mode"
          :job="job"
          @task_template_launched="$emit('task_template_launched', $event)"
          :redirect_after_launch="false">
        </task_template_wizard>
      </v-card-text>
      <v-progress-circular v-else indeterminate> </v-progress-circular>
    </v-card>
  </v-dialog>
</template>

<script>
  import Vue from "vue";
  import task_template_wizard from './task_template_wizard'
  export default Vue.extend(
    {
      components:{
        task_template_wizard: task_template_wizard
      },
      props: {
        'project_string_id':{
          default: null
        },
        'job': {
          default: null
        },
        'mode': {
          default: null
        }
      },
      name: "task_template_creation_dialog",
      computed:{
        job_id: function(){
          if(this.$props.job){
            return this.$props.job.id;
          }
        }
      },
      data (){
        return {
          is_open: false,
          loading: false
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
