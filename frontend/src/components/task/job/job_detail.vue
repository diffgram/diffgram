<template>

  <div class="job-detail-container">
    <v-tabs
      v-model="tab"
      align-with-title
      color="primary"
    >

      <v-tab
        v-for="item in items"
        :key="item.text"
      >
        <v-icon left>{{item.icon}}</v-icon>
        {{ item.text }}
      </v-tab>
      <v-tabs-items v-model="tab">

        <v-tab-item class="pt-2">
          <v_job_detail_builder v-if="$store.state.builder_or_trainer.mode == 'builder'"
                                :job_id="job_id">
          </v_job_detail_builder>


          <v_job_detail_trainer v-if="$store.state.builder_or_trainer.mode == 'trainer'"
                                :job_id="job_id">
          </v_job_detail_trainer>
        </v-tab-item>

        <v-tab-item>
          <task_template_discussions
            :project_string_id="$store.state.project.current.project_string_id"
            :task_template_id="job_id"
          ></task_template_discussions>

        </v-tab-item>

        <v-tab-item>

          <job_pipeline_mxgraph :job_id="job_id"
                                :show_output_jobs="true"
                                class="mt-4 mb-4 pb-8 pt-8">
          </job_pipeline_mxgraph>

        </v-tab-item>

      </v-tabs-items>
    </v-tabs>



  </div>

</template>

<script lang="ts">

import v_job_detail_builder from './job_detail_builder'
import v_job_detail_trainer from './job_detail_trainer'
import task_template_discussions from '../../discussions/task_template_discussions'
import job_pipeline_mxgraph from './job_pipeline_mxgraph'


import Vue from "vue"; export default Vue.extend( {
  name: 'job_detail',
  props: ['job_id'],
  components: {
    v_job_detail_builder,
    task_template_discussions,
    v_job_detail_trainer,
    job_pipeline_mxgraph
  },

  data () {
    return {
      tab: null,
      items: [
        {text: 'Oveview',
          icon: 'mdi-view-dashboard'},
        {text: 'Discussions',
          icon: 'mdi-comment-multiple'},
        {text: 'Data Pipeline',
          icon: 'mdi-folder-network'}
        ]
    }
  },
  created() {
    if(this.$route.path.endsWith('discussions')){
      this.tab = 1;
    }
  },
  computed: {
  },
  methods: {

  }
}
) </script>

<style>
  .job-detail-container{
    padding: 0 10rem;
    margin-top: 2rem;
  }
</style>
