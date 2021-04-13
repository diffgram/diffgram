<template>

  <div>


    <!-- Draft only options -->

    <!-- In the future could perhaps be more restrictive
      but for now seems like when we need to archive it we should be able to.-->
    <button_with_confirm
      @confirm_click="cancel_job_api('archive')"
      v-if="job || job_list"
      color="primary"
      icon="archive"
      :icon_style="true"
      tooltip_message="Archive"
      confirm_message="Archive"
      :disabled="loading || total_job_length_available == 0 "
      :loading="loading">
    </button_with_confirm>

    <!-- Launched options
      Note negation on list,
      Draft is excluded here because we "Archive" drafts
      instead of "Cancelling" them (Cancelled listings remain)
      -->
    <button_with_confirm
      @confirm_click="cancel_job_api('cancel')"
      v-if="job && !['cancelled', 'draft'].includes(job.status)"
      color="red"
      icon="cancel"
      :text_style="true"
      tooltip_message="Cancel"
      confirm_message="Cancel"
      :disabled="loading"
      :loading="loading">

      <template slot="content">
        <v-alert type="info"
                 >

          Careful!
          Already completed tasks will not be effected.

          This action can't be undone - consider pausing the job
          if you may want to resume it later.
        </v-alert>

      </template>

    </button_with_confirm>

    <!-- Super Admin options -->
    <button_with_confirm
      @confirm_click="cancel_job_api('delete')"
      v-if="$store.state.user.current.is_super_admin == true && job"
      color="red"
      icon="delete"
      :text_style="true"
      tooltip_message="Delete"
      confirm_message="Careful! Hard Delete"
      :disabled="loading"
      :loading="loading">

    </button_with_confirm>


    <v_error_multiple :error="error">
    </v_error_multiple>

    <v-alert type="success"
             :value="success">

    </v-alert>


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

export default Vue.extend( {
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

        mode: "cancel"


      }
    },
    computed: {
      total_job_length_available: function () {
        let length = 0
        if (this.$props.job) {length += 1}
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
        this.error = { },
        this.success = false
      },

      cancel_job_api: function (mode) {

        this.loading = true
        this.error = {}
        this.success = false

        this.mode = mode

        // todo would prefer this to be computed maybe
        this.job_id = null
        if (this.job) {
          this.job_id = this.job.id
        }

        axios.post('/api/v1/job/cancel',
          {
            'job_id': this.job_id,
            'job_list': this.job_list,
            'mode': this.mode
          })
          .then(response => {
            if (response.data.log.success == true) {

              this.success = true

              this.$emit('cancel_job_success')

            }
            this.loading = false

          })
          .catch(error => {

            if (error.response.status == 403) {
              this.$store.commit('error_permission')
            }

            this.error = error.response.data.log.error
            this.loading = false
          });
      }
    }
  }
) </script>
