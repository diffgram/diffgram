<template>
  <div id="annotator_dashboard" class="home-container">
    <v-progress-linear
      v-if="next_task_loading || load_task_list"
      height="10"
      indeterminate
      absolute
      top
      color="secondary accent-4">
    </v-progress-linear>
    <v-card class="ma-4">
      <v-container fluid>
        <v-row>
          <!--        <v-col cols="3">-->
          <!--          <v-container>-->
          <!--            <v-card>-->
          <!--              <v-container>-->

          <!--                <v-progress-linear-->
          <!--                  v-if="resume_task_loading"-->
          <!--                  height="10"-->
          <!--                  indeterminate-->
          <!--                  absolute-->
          <!--                  top-->
          <!--                  color="secondary accent-4">-->
          <!--                </v-progress-linear>-->

          <!--                <h2>Resume Last Task </h2>-->
          <!--                <div class="pa-2">-->

          <!--                  <v-layout>-->
          <!--                    <div class="d-flex align-center justify-center">-->
          <!--                      <v-btn-->
          <!--                        color="primary"-->
          <!--                        large-->
          <!--                        data-cy="resume_last_task"-->
          <!--                        :disabled="!last_task_event || resume_task_loading || (last_task_event && !last_task_event.task_id)"-->
          <!--                        @click="route_resume_task()"-->
          <!--                      >-->
          <!--                        Resume-->

          <!--                        <v-icon-->
          <!--                          right-->
          <!--                        >-->
          <!--                          mdi-replay-->
          <!--                        </v-icon>-->

          <!--                      </v-btn>-->
          <!--                    </div>-->


          <!--                    <div class="pl-4"-->
          <!--                         v-if="last_task_event-->
          <!--                        && last_file">-->

          <!--                      <file_preview_with_hover_expansion-->
          <!--                        :file="last_file"-->
          <!--                        v-if="project_string_id == last_task_event.project_string_id"-->
          <!--                        :project_string_id="last_task_event.project_string_id"-->
          <!--                        tooltip_direction="right"-->
          <!--                        @view_file_detail="route_resume_task()"-->
          <!--                      >-->
          <!--                      </file_preview_with_hover_expansion>-->

          <!--                      <div @click="route_resume_task()"-->
          <!--                           v-if="project_string_id != last_task_event.project_string_id"-->
          <!--                      >-->
          <!--                        <thumbnail-->
          <!--                          v-if="last_file.type === 'video'-->
          <!--                           || last_file.type === 'image'"-->
          <!--                          :item="last_file"-->
          <!--                        >-->
          <!--                        </thumbnail>-->
          <!--                      </div>-->


          <!--                    </div>-->

          <!--                    <div v-if="last_task_event"-->
          <!--                         class="pa-2 font-weight-light flex-column d-flex">-->
          <!--                      <div>-->
          <!--                        {{last_task_event.time_created}}-->
          <!--                      </div>-->
          <!--                      <div>-->
          <!--                        {{last_task_event.project_string_id}}-->
          <!--                      </div>-->
          <!--                      <div>-->
          <!--                        {{last_task_event.task_id}}-->
          <!--                      </div>-->
          <!--                    </div>-->


          <!--                  </v-layout>-->
          <!--                </div>-->
          <!--              </v-container>-->
          <!--            </v-card>-->
          <!--          </v-container>-->
          <!--        </v-col>-->
          <v-col cols="12">
            <v-container fluid>
              <div class="d-flex">
                <div class="">
                  <h1
                    class="clickable"
                    @click="$router.push('/job/list')"
                  >
                  <span class="font-weight-light ">
                     {{ $store.state.project.current.name }} /
                  </span>
                    <span class="font-weight-normal pl-1">
                    All My Tasks
                  </span>
                  </h1>

                </div>

                <v-spacer></v-spacer>

                <div class="pa-2" >
                  <v-btn
                    color="success"
                    large
                    data-cy="annotate_now"

                    :disabled="next_task_loading"
                    @click="api_get_next_task_annotator()"
                  >
                    Start Annotating

                    <v-icon
                      right
                    >
                      mdi-play
                    </v-icon>

                  </v-btn>
                </div>

                <div class="pa-2 pt-4">
                  <v-btn
                    color="primary"
                    small
                    outlined
                    data-cy="serach_route"
                    @click="$router.push('/job/list')"
                  >
                    Browse

                    <v-icon
                      right
                    >
                      mdi-compass
                    </v-icon>

                  </v-btn>

                </div>
              </div>
              <v-tabs v-model="tab" color="primary" style="height: 100%">
                <v-tab v-for="item in items" :key="item.text">
                  <v-icon left>{{ item.icon }}</v-icon>
                  {{ item.text }}
                </v-tab>
                <v-tabs-items v-model="tab">
                  <v-tab-item class="">
                    <task_list_headers
                      :filters="filters"
                      :total_task_count="total_task_count"
                      @refresh_task_list="refresh_task_list"
                      @update_column_list="update_column_list"
                      :project_string_id="project_string_id">

                    </task_list_headers>
                    <task_list_table
                      :project_string_id="project_string_id"
                      :task_list="task_list"
                      :column_list="column_list"
                    ></task_list_table>
                  </v-tab-item>
                  <v-tab-item>
                    <stats_panel :project_string_id="project_string_id"/>
                    <stats_task :project_string_id="project_string_id"></stats_task>
                  </v-tab-item>
                  <v-tab-item>
                    <project_discussions :project_string_id="project_string_id"></project_discussions>
                  </v-tab-item>
                </v-tabs-items>
              </v-tabs>

            </v-container>
          </v-col>
        </v-row>
      </v-container>
    </v-card>

    <v-snackbar v-model="no_task_snackbar" color="red">
      No tasks available
    </v-snackbar>

  </div>
</template>

<script lang="ts">

import axios from '../../../services/customInstance';
import {getTaskListFromProject, update_tasks_with_file_annotations} from '../../../services/tasksServices.js';
import report_dashboard from '../../report/report_dashboard';
import user_visit_history_list from '../../event/user_visit_history_list.vue'
import project_pipeline from '../../project/project_pipeline'

import Vue from "vue";
import task_list_table from "../../task/task/task_list_table.vue";
import task_list_headers from "../../task/task/task_list_headers.vue";
import Project_discussions from "../../discussions/project_discussions.vue";
import Stats_task from "../../report/stats_task.vue";
import stats_panel from "../../stats/stats_panel.vue";



export default Vue.extend({
    name: 'annotator_dashboard_me',
    components: {
      stats_panel,
      Stats_task,
      Project_discussions,
      task_list_table,
      report_dashboard,
      user_visit_history_list,
      task_list_headers,
      project_pipeline,

    },
    data() {
      return {
        no_task_snackbar: false,
        task_list: [],
        filters: {
          mode_data: 'list',
          all_my_jobs: true,
          limit_count: 10,
          page_number: 0,
          project_string_id: this.project_string_id,
        },
        items: [
          {text: "My Tasks", icon: "mdi-view-dashboard"},
          {text: "Insights", icon: "mdi-chart-areaspline"},
          {text: "Discussions", icon: "mdi-comment-multiple"},
        ],
        column_list: [
          "Status",
          "Preview",
          "AnnotationCount",
          "LastUpdated",
          "Action",
          "Job",
        ],
        next_task_loading: false,
        total_task_count: 0,
        tab: 0,
        resume_task_loading: false,
        last_file: undefined,
        load_task_list: false
      }
    },
    created() {

    },
    async mounted() {
      await this.fetch_task_list_project()
    },
    computed: {
      project_string_id: function () {
        return this.$store.state.project.current.project_string_id;
      },
      last_task_event: function () {
        if (!this.$store.state.user.history) {
          return false
        }
        let last_task_event = this.$store.state.user.history.find(
          x => x.page_name == 'task_detail')

        this.get_file_with_annotations(last_task_event)

        return last_task_event
      }
    },
    methods: {
      update_column_list: function (col_list) {
        this.column_list = col_list
      },
      refresh_task_list: async function () {
        await this.fetch_task_list_project(this.filters)
      },
      fetch_task_list_project: async function (filters = undefined) {
        try {
          this.load_task_list = true;
          if (!filters) {
            filters = {
              mode_data: 'list',
              project_string_id: this.project_string_id,
              all_my_jobs: true
            }
          }

          const [task_list_data, err] = await getTaskListFromProject(this.project_string_id, filters)
          this.task_list = task_list_data.task_list

          update_tasks_with_file_annotations(this.task_list)

          this.total_task_count = task_list_data.total_count
          if (err) {
            console.error(err)
            return
          }
        } catch (e) {
          console.error(e)
        } finally {
          this.load_task_list = false
        }
      },
      route_resume_task: function () {
        this.resume_task_loading = true
        const routeData = `/task/${this.last_task_event.task_id}`;
        this.$router.push(routeData)
      },

      async get_file_with_annotations(last_task_event) {
        if (!last_task_event) {
          return
        }
        let url = '/api/v1/task/' + last_task_event.task_id + '/annotation/list';
        this.get_annotations_error = {}
        this.get_annotations_loading = true
        this.last_file = undefined

        try {
          const response = await axios.post(url, {})
          this.last_file = response.data.file_serialized
        } catch (error) {
          console.debug(error);
          this.get_annotations_error = this.$route_api_errors(error)
        } finally {
          this.get_annotations_loading = false
        }
        return
      },

      api_get_next_task_annotator: async function () {
        try {
          this.next_task_loading = true
          const response = await axios.post(
            `/api/v1/project/${this.project_string_id}/task/next`, {});
          if (response.status === 200 && response.data.task) {
            let task = response.data.task
            const routeData = `/task/${task.id}`;
            this.$router.push(routeData)
          } else {
            this.no_task_snackbar = true
          }
        } catch (e) {
          console.error(e);
        } finally {
          this.next_task_loading = false;
        }
      }

    }
  }
) </script>

<style scoped>
.home-container {
  padding: 0 10rem;
}
</style>

