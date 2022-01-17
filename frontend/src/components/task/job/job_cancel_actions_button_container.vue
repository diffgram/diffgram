<template>

  <div class="mt-4 d-flex justify-end flex-column">
    <div class="d-flex justify-end align-center">
      <button_with_confirm

        @confirm_click="cancel_job_api('archive')"
        v-if="job || job_list"
        color="white"
        button_color="error"
        icon="archive"
        tooltip_message="Archive"
        button_text="Archive Task Template"
        confirm_message="Careful! This will archive the Task Template and all the related tasks in the task list."
        :disabled="loading || total_job_length_available == 0 "
        :loading="loading">
      </button_with_confirm>
      <span class="mr-6"></span>
      <button_with_confirm

        @confirm_click="cancel_job_api('cancel')"
        v-if="job && !['cancelled', 'draft'].includes(job.status)"
        color="white"
        button_color="warning"
        icon="cancel"
        button_text="Cancel Task Template"
        tooltip_message="Cancel"
        confirm_message="Cancel"
        :disabled="loading"
        :loading="loading">

        <template slot="content">
          <v-alert type="info">

            Careful!
            Already completed tasks will not be effected.

            This action can't be undone.
          </v-alert>

        </template>

      </button_with_confirm>
    </div>


    <div class="mt-4">
      <v_error_multiple :error="error">
      </v_error_multiple>

      <v-alert type="success"
               :dismissible="true"
               :value="success">
        {{ success_text }}
      </v-alert>
    </div>


  </div>


</template>

<script lang="ts">

import axios from 'axios';


import Vue from "vue";

/*
  * Jan 20, 2020
  *    Question, directionally, should this be out generic
  *    "updates to job" abstraction?
  *
  *
  *
  */

export default Vue.extend({
    name: 'job_cancel',
    props: {
      'job': {
        default: null
      },
      'job_list': {
        default: null,
        type: Array
      }

    },

    data() {
      return {


        loading: false,
        error: {},
        success: false,
        success_text: '',

        mode: "cancel"


      }
    },
    computed: {
      total_job_length_available: function () {
        let length = 0
        if (this.$props.job) {
          length += 1
        }
        if (this.$props.job_list) {
          length += this.$props.job_list.length
        }
        return length
      }
    },
    created() {

    },
    watch: {
      //'$job' : 'reset'
    },
    methods: {

      reset: function () {
        this.loading = false,
          this.error = {},
          this.success = false
      },
      go_to_task_templates_list: function () {
        this.$router.push("/job/list");
      },
      cancel_job_api: async function (mode) {
        this.success_text = ''
        this.loading = true
        this.error = {}
        this.success = false

        this.mode = mode

        // todo would prefer this to be computed maybe
        this.job_id = null
        if (this.job) {
          this.job_id = this.job.id
        }

        try {

          const response = await axios.post('/api/v1/job/cancel',
            {
              'job_id': this.job_id,
              'job_list': this.job_list,
              'mode': this.mode
            })
          if (response.data.log.success == true) {

            this.success = true
            if(mode === 'cancel'){
              this.success_text = 'Job Canceled Successfully'
            }
            else if(mode === 'archive'){
              this.success_text = 'Job Archived Successfully'
            }

            await new Promise(resolve => setTimeout(resolve, 1500));
            this.$emit('cancel_job_success')
            this.go_to_task_templates_list();

          }
        } catch (error) {
          if (error.response.status == 403) {
            this.$store.commit('error_permission')
          }
          this.error = error.response.data.log.error
        } finally {
          this.loading = false
        }
      }
    }
  }
) </script>
