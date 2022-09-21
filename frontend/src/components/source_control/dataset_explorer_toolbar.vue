<template>
  <div class="ds-explorer-toolbar-container d-flex align-center justify-end pr-8">
    <div v-if="selected_files.length > 0">
      <v-chip small color="success">
        <span v-if="!loading">Selected: <strong>{{ selected_files.length }}</strong></span>
        <span v-else> <v-progress-circular size="12" indeterminate></v-progress-circular></span>
      </v-chip>
    </div>

    <div class="mr-2">
      <button_with_menu
        icon="mdi-plus-network"
        :icon_style="true"
        :disabled="selected_files.length === 0"
        tooltip_message="Create tasks from selection"
        color="success"
        :close_by_button="true"
        menu_direction="top"
        action_icon="mdi-upload-network-outline"
        action_message="Create tasks"
        action_color="success"
        @action_clicked="add_tasks_to_task_template"
      >

        <template slot="content">
          <v-card elevation=0>
            <v-card-title>Select Task template</v-card-title>
            <v-card-text class="text--primary">
              <job_select v-model="selected_job" label="Select Task Template"></job_select>
            </v-card-text>
          </v-card>
        </template>

      </button_with_menu>
    </div>
    <div class="mr-4">
      <v-checkbox
        v-model="select_all"
        @change="select_all_files"
        :label="`Select All`"
      ></v-checkbox>
    </div>


    <div>
      <v-chip small color="secondary">
        <span v-if="!loading">Total: <strong>{{ file_count }}</strong></span>
        <span v-else> <v-progress-circular size="12" indeterminate></v-progress-circular></span>
      </v-chip>
    </div>

  </div>
</template>

<script>
import Vue from "vue";
import job_select from '@/components/task/job/job_select.vue'
import {add_files_to_task_template} from '@/services/taskTemplateService'

export default Vue.extend({
  name: "dataset_explorer_toolbar",
  components: {
    job_select
  },
  props: [
    'project_string_id',
    'selected_files',
    'file_count',
    'loading',
    'query',
  ],
  async mounted() {

  },
  data: function () {
    return {
      select_all: false,
      selected_job: null
    }
  },
  watch: {},
  computed: {},
  methods: {
    add_tasks_to_task_template: async function () {
      if(!this.selected_job){
        this.$store.commit('display_snackbar', {
          text: `Please select a job before submitting`,
          color: 'error'
        })
        return
      }
      let task_template_id = this.selected_job.id
      if (this.select_all) {
        let query = ''
        if (this.$props.query){
          query = this.$props.query
        }
        var [data, err] = await add_files_to_task_template(task_template_id, undefined, query)
      } else {
        let file_id_list = this.selected_files.map(elm => elm.id)
        var [data, err] = await add_files_to_task_template(task_template_id, file_id_list, undefined)
      }
      if (err != null){
        this.$store.commit('display_snackbar', {
          text: `Error adding files to dataset ${err}`,
          color: 'error'
        })
        return
      }
      if(data){
        this.$store.commit('display_snackbar', {
          text: `Tasks are being created...`,
          color: 'success'
        })
      }
    },
    select_all_files: function () {
      this.$emit('select_all')
    }
  }

})
</script>

<style>
.ds-explorer-toolbar-container {
  width: 100%;
  border: solid 1px #e0e0e0;
  height: 35px !important;

}
</style>
