<template>
  <div v-cloak>
    <div v-if="['job_edit'].includes(mode_view)">
      {{ job.status }}
    </div>

    <div v-if="['job_detail'].includes(mode_view)">


      <!-- For now treating the
        general "job only" attributes
        as *different* from something that updates tasks
        too like the labels thing. -->

      <v-layout>
        <job_type :type="job.type"
                  :size="40"
                  class="pa-2">
        </job_type>

        <h2 class="pa-2"
            v-if="edit_job == false">
          {{ job.name }}

        </h2>
        <v-text-field
          v-if="edit_job == true"
          v-model="job.name"
          @input="has_changes = true"
          solo
          flat
          style="font-size: 18pt"
                >
        </v-text-field>

        <div class="pa-2">
          <tooltip_button
              v-if="edit_job == false"
              tooltip_message="Edit Name"
              @click="edit_job = true"
              icon="edit"
              :icon_style="true"
              color="primary">
          </tooltip_button>
        </div>


        <button_with_confirm
          v-if="edit_job == true"
          @confirm_click="api_update_job()"
          color="primary"
          icon="save"
          :icon_style="true"
          :large="true"
          tooltip_message="Save Name Updates"
          confirm_message="Confirm"
          :loading="loading"
          :disabled="loading">
        </button_with_confirm>

        <v-spacer> </v-spacer>

        <!-- output_dir_action -->
        <icon_from_regular_list
            :item_list="output_dir_action_icon_list"
            :value="job.output_dir_action">
        </icon_from_regular_list>

        <icon_from_regular_list
            :item_list="share_icon_list"
            :value="job.share_type">
        </icon_from_regular_list>


      </v-layout>

      <!-- TODO job status component -->
      <h3>
        {{ job.status }}  tasks remaining {{ job.tasks_remaining }}
      </h3>

      <div class="pa-2">
      <v-progress-linear v-model="job.percent_completed">
      </v-progress-linear>
      </div>
      <!-- May want some fancier render
            thing for view only but I think this works for now-->
    <v-layout>

      <label_select_only
        v-if="job.label_dict && job.label_dict.label_file_list_serialized"
        label_prompt="Locked Schema"
        :mode=" 'multiple' "
        :view_only_mode="label_select_view_only_mode"
        :label_file_list_prop="job.label_dict.label_file_list_serialized"
        :load_selected_id_list="job.label_dict.label_file_list"
        :request_refresh_from_project="request_refresh_labels"
          @label_file="update_label_file_list = $event"
                          >
      </label_select_only>

      <!-- We assume in general we want to just view this information
        so we have this extra "lock" by requiring a click to change it to
        be editable.
        Also some of it may change
        -->

      <!-- Edit unlock -->
      <div class="pa-2">
        <tooltip_button
            v-if="label_select_view_only_mode == true"
            tooltip_message="Edit Locked Schema"
            @click="request_refresh_labels = Date.now(),
                    label_select_view_only_mode = false"
            icon="edit"
            :icon_style="true"
            color="primary">
        </tooltip_button>
      </div>

      <!-- Save Edit -->

      <!-- In context of label updates
        but a bit more to think about here...
          wording could be a bit sensitive-->
      <button_with_confirm
        v-if="label_select_view_only_mode == false"
        @confirm_click="api_update_job()"
        color="primary"
        icon="save"
        :icon_style="true"
        :large="true"
        tooltip_message="Save & Update Tasks"
        confirm_message="Save & Update All Tasks"
        :loading="loading"
        :disabled="loading">
      </button_with_confirm>

    </v-layout>
            
    <v-alert
            v-if="label_select_view_only_mode == false"
            type="info"
            icon="mdi-lock">
      Schema is locked by default for each group of Tasks. To apply the new desired Schema to this set of tasks,
      select it here and then click save.
      Note Attributes follow labels, so if an attribute for a label has changed, simply click save directly.
      <a style="color: white"
          href="https://diffgram.readme.io/docs/updating-existing-tasks" > Docs </a>
    </v-alert>

    <v_error_multiple :error="error">
    </v_error_multiple>

    <v_info_multiple :info="info">
    </v_info_multiple>



    </div>

    <div v-if="job.td_api_trainer_basic_training == true">
      <h2> <v-icon>mdi-heart</v-icon> Basic Training </h2>
    </div>
  </div>
</template>


<script lang="ts">

import axios from 'axios';
import job_type from './job_type';
import label_select_only from '../../label/label_select_only.vue'
import { route_errors } from '../../regular/regular_error_handling'

import Vue from "vue";

export default Vue.extend( {
  name: 'job_info_builder',
  components: {
    job_type,
    label_select_only
  },
  props: {
    'job_id': {
      default: null
    },
    'mode_data': {
      default: null     // job_edit, job_detail
    },
    // not clear on difference between use for view and data in this context yet
    'mode_view': {
      default: null     // job_edit, job_detail
    }
  },
  data() {
    return {
      loading: false,

      share_icon_list : [
        {
          'display_name': 'Shared with Project',
          'name': 'project',
          'icon': 'mdi-lightbulb',
          'color': 'blue'
        },
        {
          'display_name': 'Shared with Org',
          'name': 'org',
          'icon': 'mdi-domain',
          'color': 'green'
         }
      ],

      output_dir_action_icon_list : [
        {
          'display_name': 'Output Dataset Action: Copy',
          'name': 'copy',
          'icon': 'mdi-content-copy',
          'color': 'blue'
        },
        {
          'display_name': 'Output Dataset Action: Move',
          'name': 'move',
          'icon': 'mdi-file-move',
          'color': 'green'
         },
         {
          'display_name': 'Output Dataset Action: None',
          'name': 'nothing',
          'icon': 'mdi-circle-off-outline',
          'color': 'gray'
         }
      ],

      request_refresh_labels: null,

      label_select_view_only_mode: true,

      has_changes: false,
      edit_job: false,

      info: {},
      error: {},

      job: {
        percent_completed: 0,
        label_dict: null
      },

      update_label_file_list: null,

    }
  },
  computed: {

  },

  watch: {

  },

  created() {

    this.job_builder_info()

  },
  methods: {
    job_builder_info: function () {

      this.loading = true

      axios.post(
        '/api/v1/job/' + this.job_id +
        '/builder/info', {
          'mode_data': this.mode_data
        }
      ).then(response => {

        if (response.data.log.success == true) {

          this.job = response.data.job
          this.$emit('job_info', this.job)

        }

        this.loading = false

      })
        .catch(error => {

          if (error.response.status == 403) {
            this.$store.commit('error_permission')
          }

          console.log(error);
          this.loading = false

        });
    },

  api_update_job: function () {
  /*
    * Assumes one job at a time
    *
    * Assumes fields NOT being updated are Null!
    *  So for example update_label_file_list starts off as null
    *  and when update goes to check it, if it's null it won't touch
    *  it.
    *
    *  This can be verified sorta by the info dict returned.
    *
    *  Not quite clear the right way to "reset" this so to speak.
    *
    */


  this.loading = true
  this.error = {}
  this.info = {}

  axios.post('/api/v1/project/' + this.$store.state.project.current.project_string_id +
        '/job/update', {

    job_id : parseInt(this.job_id),
    label_file_list: this.update_label_file_list, // see assumptions on null in note above
    name: this.job.name

  }).then(response => {


    this.loading = false
    this.info = response.data.log.info
    this.edit_job = false
    this.has_changes = false

    // careful to reset
    this.update_label_file_list = null

  })
  .catch(error => {
    this.loading = false
    this.error = route_errors(error)

  });

},



  }
}

) </script>
