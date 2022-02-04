<template>
  <div class="d-flex flex-column">

    <v-container class="d-flex flex-wrap justify-start"
                 fluid>

      <v-card v-for="job in ordered_job_list"
              v-bind:key="job.id"
              data-cy="job-card"
              id="card-list"
              width="350px"
              style="position: relative"
              class="ma-4 d-flex flex-column job-card"
              elevation="1"
      >

        <div style="position: absolute;
                  top: 0;
                  left: 0"
             class="text-right pa-2 mb-8">
          <v-chip small v-if="job.type === 'exam_template'" color="secondary"><v-icon>mdi-test-tube</v-icon> Exam </v-chip>
          <v-chip small v-if="job.type === 'examination'" color="secondary lighten-3"><v-icon>mdi-test-tube</v-icon> Examinaton </v-chip>
        </div>
        <div style="position: absolute;
                  top: 0;
                  right: 0"
             class="text-right pa-2">

          <tooltip_button
            tooltip_message="Pin"
            v-if="!job.is_pinned"
            icon="mdi-pin-outline"
            :icon_style="true"
            :bottom="true"
            :disabled="pin_loading"
            :loading="pin_loading"
            color="primary"
            @click="pin_job(job)"
          >
          </tooltip_button>

          <tooltip_button
            tooltip_message="Pinned"
            v-else
            icon="mdi-pin"
            :icon_style="true"
            :bottom="true"
            :disabled="pin_loading"
            :loading="pin_loading"
            color="primary"
            @click="pin_job(job)"
          >
          </tooltip_button>
        </div>

        <v-card-title
          @click="job_detail_page_route_by_status(job)"
          :class="{'mt-4': ['exam_template', 'examination'].includes(job.type)}"
          style="cursor: pointer; overflow-wrap: anywhere; padding-right: 3rem">
          <span class="job-title">
          {{job.name | truncate(40)}}
          </span>
        </v-card-title>

        <v-card-subtitle>
          <v-chip :color="status_color(job.status)" x-small>{{job.status | capitalize }}</v-chip>
          <span>Created: {{job.time_created | moment("DD-MM-YYYY H:mm:ss a")}}</span>
        </v-card-subtitle>
        <v-card-text class="flex-grow-2">
          <v-container fluid class="d-flex flex-column pa-0">

            <v-row>
              <v-col cols="4">
                <div v-if="job.file_count_statistic"
                     class="d-flex flex-column">
                  <span class="font-weight-bold text-center">{{job.file_count_statistic}}</span>
                  <span class="text-center">Files</span>
                </div>
                <div v-else class="d-flex flex-column">
                  <span class="font-weight-bold text-center">0</span>
                  <span class="text-center">Files</span>
                </div>
              </v-col>

              <v-col cols="4">
                <div v-if="job.stat_count_available"
                     class="d-flex flex-column">
                  <span class="primary--text font-weight-bold text-center">{{job.stat_count_available}}</span>
                  <span class="primary--text text-center">Active</span>
                </div>
                <div v-else class="d-flex flex-column">
                  <span class="primary--text font-weight-bold text-center">0</span>
                  <span class="primary--text text-center">Active</span>
                </div>
              </v-col>

              <v-col cols="4">
                <div v-if="job.stat_count_complete"
                     class="d-flex flex-column">
                  <span class="success--text font-weight-bold text-center">{{job.stat_count_complete}}</span>
                  <span class="success--text text-center">Complete</span>
                </div>
                <div v-else class="d-flex flex-column">
                  <span class="success--text font-weight-bold text-center">0</span>
                  <span class="success--text text-center">Complete</span>
                </div>
              </v-col>
            </v-row>

            <v-row class="mb-4" dense>
              <v-col cols="12" class="d-flex pa-0" v-if="job.member_list_ids.length > 0">
                <v_user_icon v-if="member_id != 'all'"
                             :member_id="member_id"
                             v-for="member_id in job.member_list_ids"
                             v-bind:key="member_id"
                             :size="22"
                             fontSize="12px !important"
                             class="pr-1">
                </v_user_icon>
              </v-col>
              <!--
              <v-col cols="12" v-else>
                <v-icon color="primary"
                        left >
                    mdi-select-all
                </v-icon>
                All Users
              </v-col>
              -->
            </v-row>

            <v-row class="pl-4">
              <!-- Copy and paste from job list but changed to job-->
              <div  style="max-width: 200px" class="d-flex flex-wrap"
                    v-if="job && job.attached_directories_dict && job.attached_directories_dict.attached_directories_list">
                <div class="dir d-flex align-center  justify-center ml-1"
                     v-for="dir in job.attached_directories_dict.attached_directories_list"
                     v-bind:key="dir.id"
                >
                  <v-icon color="primary">mdi-folder</v-icon>
                  <p class="ma-0">{{ dir.nickname }}</p>
                </div>

              </div>

              <div  style="max-width: 200px" class="d-flex flex-wrap"
                    v-if="job && job.completion_directory">
                <div class="dir d-flex align-center  justify-center"
                     v-if="job.completion_directory.nickname">
                  <v-icon color="primary">mdi-folder</v-icon>
                  <p class="ma-0">{{ job.completion_directory.nickname }}</p>
                </div>
              </div>
            </v-row>

            <v-row class="mb-4" dense>
              <v-col cols="12" class="pa-0">

                <label_select_only
                  v-if="job.label_dict &&
                        job.label_dict.label_file_list_serialized"
                  :limit="5"
                  :mode=" 'multiple' "
                  :label_prompt="null"
                  :view_only_mode="true"
                  :label_file_list_prop="job.label_dict.label_file_list_serialized"
                  :load_selected_id_list="job.label_dict.label_file_list"
                >
                </label_select_only>

              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <v-card-actions style="
                          position: absolute;
                          bottom: 0;
                          right: 0"
        >

          <v-container class="pa-0">
            <v-row dense style="border-top: 2px solid #e6e6e6">

              <div class="pl-2 pt-1">

              </div>
              <tooltip_button datacy='resync_button'
                              tooltip_message="Resync Missing Files"
                              icon="mdi-refresh"
                              color="primary"
                              :icon_style="true"
                              @click="confirm_resync_dialog_open = true">
              </tooltip_button>
              <v-dialog
                v-model="confirm_resync_dialog_open"
                max-width="450"
              >
                <v-card>
                  <v-card-title class="text-h5">
                    Are you sure you want to sync all files?
                  </v-card-title>

                  <v-card-text>
                    This will create tasks for any missing or pending files in the directories attached to this job.
                    This can take several minutes.
                  </v-card-text>

                  <v-card-actions>
                    <v-spacer></v-spacer>

                    <v-btn
                      color="red darken-1"
                      text
                      @click="confirm_resync_dialog_open = false"
                    >

                      Cancel

                    </v-btn>
                    <v-btn
                      color="green darken-1"
                      text
                      :loading="loading_resync_job"
                      @click="resync_job(job)"
                    >
                      Resync All Files From Job
                    </v-btn>
                  </v-card-actions>
                </v-card>
              </v-dialog>
              <tooltip_button datacy='view_button'
                              tooltip_message="View"
                              icon="mdi-eye"
                              color="primary"
                              :icon_style="true"
                              @click="job_detail_page_route_by_status(job)">
              </tooltip_button>


              <tooltip_button datacy='next_task_button'
                              tooltip_message="Go To Next Pending Task"
                              icon="mdi-page-next"
                              color="primary"
                              :icon_style="true"
                              :disabled="!job.stat_count_available || job.stat_count_available === 0"
                              @click="go_to_next_task(job)">
              </tooltip_button>


              <tooltip_button datacy='discussions_button'
                              tooltip_message="Discussions"
                              icon="mdi-comment-text-multiple-outline"
                              color="primary"
                              :icon_style="true"
                              @click="$router.push(`/job/${job.id}/discussions`)">
              </tooltip_button>


              <tooltip_button datacy='pipeline_button'
                              tooltip_message="Task Template Pipeline"
                              icon="mdi-relation-many-to-many"
                              color="primary"
                              :icon_style="true"
                              @click="open_task_template_pipeline_dialog(job)">
              </tooltip_button>

            </v-row>
          </v-container>
        </v-card-actions>
      </v-card>

      <job_pipelines_dialog ref="job_pipelines_dialog" :job="selected_job"></job_pipelines_dialog>
    </v-container>
    <v-snackbar v-model="show_resync_snackbar" timeout="5000" color="success" shaped >
      Job Resyncing, missing tasks are being created.
    </v-snackbar>

  </div>

</template>

<script lang="ts">
  import Vue from "vue";
  import axios from 'axios';
  import job_pipelines_dialog from '../job/job_pipelines_dialog';
  import label_select_only from '../../label/label_select_only.vue'

  export default Vue.extend({
      name: 'job_list_card_display',
      components: {
        job_pipelines_dialog,
        label_select_only
      },
      props: {
        'project_string_id': {
          default: null
        },
        'job_list': {
          default: null
        },
        'loading':{
          'default': false
        }

      },
      watch: {
        '$route': 'mount'
      },
      data() {
        return {
          selected_job: undefined,
          pin_loading: false,
          confirm_resync_dialog_open: false,
          show_resync_snackbar: false,
          loading_resync_job: false,
        }
      },
      mounted: function () {

      },
      computed: {
        ordered_job_list: function(){
          // Prioritize pinned jobs

          return this.job_list.sort((a,b) =>{
            if(a.is_pinned === b.is_pinned){
              return 0
            }
            if(a.is_pinned){
              return -1
            }
            else{
              return 1
            }
          })
        },
        project_member_list: function () {
          return this.$store.state.project.current.member_list
        },
        headers_view: function () {

          // Not sure if want to use vuex directly here
          // Or local variable instead
          // Since changing modes would effect other stuff

          if (this.$store.state.builder_or_trainer.mode == "trainer") {
            return this.headers_trainer
          }
          if (this.$store.state.builder_or_trainer.mode == "builder") {
            return this.headers_builder
          }


        },
        current_user: function () {
          return this.$store.state.user.current;
        }
      },

      created() {

      },

      filters: {
        truncate: function (value, numchars) {
          return value && value.length > numchars ? value.substring(0, numchars) + "..." : value
        },
        capitalize: function (value) {
          if (!value) return ''
          value = value.toString()
          return value.charAt(0).toUpperCase() + value.slice(1)
        }
      },
      methods: {
        resync_job: async function(job){
          try {
            this.loading_resync_job = true;
            const response = await axios.post(`/api/v1/project/${this.$props.project_string_id}/job/resync`, {
              'task_template_id': job.id,
              'project_string_id': this.$props.project_string_id
            })
            if (response.data.resync_result) {
              this.show_resync_snackbar = true;
            }
          } catch (error) {
            console.error(error)
          }
          finally{
            this.loading_resync_job = false;
          }
        },
        job_detail_page_route_by_status(job) {
          if (job.status == "draft") {
            this.$router.push("/job/new/" + job.id)
            return
          }
          if(job.type === 'exam_template'){
            this.$router.push(`/${this.$props.project_string_id}/exam/${job.id}`)
          }
          else if(job.type === 'examination'){
            this.$router.push(`/${this.$props.project_string_id}/examination/${job.id}`)
          }
          else{
            this.$router.push("/job/" + job.id)
          }


        },
        pin_job: async function(job){
          try{
            this.pin_loading = true
            const response = await axios.post(`/api/v1/job/${job.id}/pin`, {})
            this.pin_loading = false
            if(response.status === 200){
              job.is_pinned = response.data.job.is_pinned;
            }
          }
          catch (e) {
            this.pin_loading = false
            console.error(e)
          }
        },
        go_to_next_task: async function (job) {
          try {
            const response = await axios.post(`/api/v1/job/${job.id}/next-task`, {
              'direction': 'next',
              'project_string_id': this.$props.project_string_id
            })
            if (response.data.task) {
              this.$router.push(`/task/${response.data.task.id}`)
            }
          } catch (error) {
            console.error(error)
          }
        },
        open_task_template_pipeline_dialog: function (job) {
          this.selected_job = job;
          this.$refs.job_pipelines_dialog.open();
        },
        status_color: function (status) {
          if (status === 'active') {
            return 'success'
          } else if (status === 'archived') {
            return 'error'
          } else if (status === 'draft') {
            return 'warning'
          } else {
            return 'primary'
          }
        },
      },
    }
  ) </script>
<style>

</style>
