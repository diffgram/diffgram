<template>
  <div>

    <main_menu v-if="may_edit"
               height="250">

      <template slot="second_row">

        <v-toolbar
          style="border-top: 1px solid #e0e0e0"
          dense
          elevation="1"
          fixed
          height="50px"
        >
          <v-toolbar-items>
            <standard_chip
              v-if="report_template && report_template.id != null"
              :message="`${report_template.id}`"
              tooltip_message="ID"
              color="grey"
              tooltip_direction="bottom"
              :small="true"
            >
            </standard_chip>
            <v-text-field
              class="ma-0"
              style="font-size: 18pt"
              v-model="report_template.name"
              @input="has_changes = true"
              placeholder="My Report"
              solo
              flat
            >
            </v-text-field>


            <standard_button tooltip_message="Save & Refresh Report"
                            @click="save_and_run_report"
                            icon="mdi-refresh"
                            :disabled="loading"
                            :text_style="true"
                            :large="true"
                            color="primary">
            </standard_button>

            <standard_button tooltip_message="More Filters & Configs"
                            @click="open_extra_filters_dialog"
                            icon="mdi-filter"
                            :disabled="!['instance'].includes(report_template.item_of_interest)"
                            :text_style="true"
                            :large="true"
                            color="primary">
            </standard_button>
            <v-dialog v-model="show_filters_dialog"
                      width="800">
              <v-card>
                <v-card-title>More Filters:</v-card-title>
                <v-card-text>
                  <v-container>
                    <h2>Labels & Instances</h2>

                  </v-container>
                </v-card-text>
              </v-card>
            </v-dialog>

            <standard_button tooltip_message="Save"
                            @click="save_report(true)"
                            icon="save"
                            :text_style="true"
                            :large="true"
                            :disabled="!has_changes"
                            color="primary">
            </standard_button>

            <standard_button
              tooltip_message="Back to Report List"
              @click="$router.push('/reports/list')"
              icon="list"
              :icon_style="true"
              :large="true"
              color="primary">
            </standard_button>

            <standard_button
              tooltip_message="Download as CSV"
              @click="download_csv"
              icon="mdi-download"
              color="primary"
              :disabled="loading"
              :text_style="true"
              :large="true"
            >
            </standard_button>

            <div class="pa-2">
              <div v-if="has_changes">
                Changes detected.
              </div>
              <div v-else>
                No changes.
              </div>
            </div>

            <div class="pa-2 pl-4 pr-4">
              <standard_chip
                :message="`${report.count}`"
                tooltip_message="Sum"
                color="primary"
                tooltip_direction="bottom">
              </standard_chip>

            </div>

            <div class="pa-2">
              <v-checkbox v-if="$store.state.user.current.is_super_admin"
                          v-model="report_template.diffgram_wide_default"
                          label="Diffgram Default"
                          @change="has_changes = true"
                          :disabled="loading"
              >
              </v-checkbox>
            </div>

            <div class="pa-2">
              <v-checkbox v-model="report_template.is_visible_on_report_dashboard"
                          label="Show on Dashboard"
                          @change="has_changes = true"
                          :disabled="loading"
              >
              </v-checkbox>
            </div>

            <div class="pa-2">
              <v-checkbox v-model="report_template.archived"
                          label="Archived"
                          @change="has_changes = true"
                          :disabled="loading"
              >
              </v-checkbox>
            </div>

          </v-toolbar-items>
        </v-toolbar>
      </template>

      <template slot="third_row">

        <v-toolbar
          style="border-top: 1px solid #e0e0e0"
          elevation="1"
          fixed
          height="75px"
        >
          <v-toolbar-items>

            <!-- base_class -->
            <v-row>
              <v-col cols="2">
                <diffgram_select
                  class="pa-4"
                  :item_list="item_of_interest_list"
                  v-model="report_template.item_of_interest"
                  label="Item of Interest"
                  :disabled="loading"
                  @change="on_change_item_of_interest"
                >
                </diffgram_select>
              </v-col>

              <v-col cols="2">
                <!-- Period -->
                <diffgram_select
                  style="min-width: 200px"
                  class="pa-4"
                  :item_list="period_list"
                  v-model="report_template.period"
                  label="Period"
                  :disabled="loading"
                  @change="has_changes = true"
                >
                </diffgram_select>
              </v-col>

              <v-col cols="2">
                <!-- Period -->
                <diffgram_select
                  class="pa-4"
                  :item_list="current_group_by_list"
                  v-model="report_template.group_by"
                  label="Group by"
                  :disabled="loading"
                  @change="has_changes = true"
                >
                </diffgram_select>
              </v-col>

               <v-col cols="2">
                      <diffgram_select
                        class="pa-4"
                        :item_list="second_group_by_list"
                        v-model="report_template.second_group_by"
                        :clearable="true"
                        label="Second Group by"
                        :disabled="loading"
                        @change="has_changes = true"
                      >
                      </diffgram_select>
                </v-col>

              <!--
                <diffgram_select
                  class="pa-4"
                  :item_list="scope_icon_list"
                  v-model="report_template.scope"
                  label="Permission Scope"
                  :disabled="true || loading"
                  @change="has_changes = true"
                >
                </diffgram_select>
              -->
              <v-col cols="2">
                <!-- View Type -->
                <diffgram_select
                  class="pa-4"
                  :item_list="view_type_list"
                  v-model="report_template.view_type"
                  label="View"
                  :disabled="loading"
                  @change="has_changes = true"
                >
                </diffgram_select>

              </v-col>

              <v-col cols="2">
                <!-- View view_sub_type -->
                <diffgram_select
                  class="pa-4"
                  v-if="report_template.view_type == 'chart'"
                  :item_list="view_sub_type_list"
                  v-model="report_template.view_sub_type"
                  label="Type"
                  :disabled="loading"
                  @change="has_changes = true"
                >
                </diffgram_select>
              </v-col>

            </v-row>
          </v-toolbar-items>
        </v-toolbar>

      </template>

      <template slot="forth_row">

        <!-- generally try to keep this to "concrete" filters,
          so can form a visual distinction in comparison to row above this
          which are the "abstract" filters -->

        <v-toolbar
          style="border-top: 1px solid #e0e0e0"
          elevation="1"
          fixed
          height="75px"
        >
          <v-toolbar-items>

            <v-row class="d-flex justify-start align-center">
              <v-col cols="3"   v-if="['file', 'task', 'instance'].includes(report_template.item_of_interest)">
                <div style="min-width: 200px" class="pa-4">
                  <job_select v-model="job"

                              :disabled="loading || !['file', 'task', 'instance'].includes(report_template.item_of_interest)"
                              @change="set_job"
                              :select_this_id="job_select_this_id"
                  >

                  </job_select>
                </div>
              </v-col>
              <v-col cols="3" v-if="['task'].includes(report_template.item_of_interest)">
                <div style="min-width: 200px; max-width: 300px" class="pa-4">
                  <diffgram_select
                    v-if="['task'].includes(report_template.item_of_interest)"
                    class="pa-4"
                    :item_list="task_status_filter"
                    v-model="report_template.task_event_type"
                    label="Task Status"
                    :disabled="loading"
                    @change="has_changes = true"
                  >
                  </diffgram_select>
                </div>
              </v-col>
              <v-col cols="3"   v-if="['instance'].includes(report_template.item_of_interest)">
                <div style="min-width: 200px" class="pa-4">
                  <v-text-field

                    type="number"
                    clearable
                    @change="has_changes = true"
                    v-model="report_template.task_id"
                    label="Filter by Task ID">
                  </v-text-field>
                </div>
              </v-col>
              <v-col cols="3">
                <div style="min-width: 200px; max-width: 300px" class="pa-4">
                  <member_select
                    v-model="member_list"
                    :label="member_list_label"
                    multiple
                    :show_names_on_selected="true"
                    @change="has_changes = true"
                    :allow_all_option="true"
                    :member_list="$store.state.project.current.member_list">
                  </member_select>

                </div>
              </v-col>
              <v-col cols="3">
                <div style="min-width: 200px" class="pa-4">
                  <label_select_only
                    :project_string_id="$store.state.project.current.project_string_id"
                    @selected_ids_only="report_template.label_file_id_list = $event,
                                 has_changes = true"
                    :load_selected_id_list="report_template.label_file_id_list"
                    :mode=" 'multiple' "
                    :disabled="loading"
                    :show_select_all="false"
                  >
                  </label_select_only>
                </div>
              </v-col>
            </v-row>
          </v-toolbar-items>
        </v-toolbar>

      </template>

    </main_menu>



    <v-alert type="info"
             v-if="!loading && values.length == 0 && report.count ==0"
             dismissible>
      No results. <br>
      Is (time period, project) correct?
    </v-alert>

    <v-card v-if="may_edit == false"
            elevation="0">
      <v-container>

        <v-layout>
          <!-- item_of_interest -->
          <icon_from_regular_list
            :item_list="item_of_interest_list"
            :value="report_template.item_of_interest"
          >
          </icon_from_regular_list>

          <icon_from_regular_list
            :item_list="period_list"
            :value="report_template.period"
          >
          </icon_from_regular_list>

          <icon_from_regular_list
            :item_list="group_by_list"
            :value="report_template.group_by"
          >
          </icon_from_regular_list>

          <v-spacer></v-spacer>

          <tooltip_icon
            v-if="report_template.diffgram_wide_default"
            tooltip_message="Default"
            icon="mdi-check-circle"
            color="primary">
          </tooltip_icon>
        </v-layout>

      </v-container>
    </v-card>

    <v-card class="mt-4" v-if="report_template.view_type == 'chart' " elevation="0">
      <v-container>

        <!-- DATE -->
        <div v-if="report_template.group_by == 'date'">

          <line_chart
            :chart-data="datacollection"
            :options="options"
            v-if="report_template.view_sub_type == 'line' &&
                report_template.group_by == 'date' ">
          </line_chart>

          <bar_chart
            v-if="report_template.view_sub_type == 'bar'
                || !report_template.view_sub_type"
            :chart-data="datacollection"
            :options="bar_chart_options_time_series">
          </bar_chart>

        </div>


        <!-- NOT Date -->
        <div v-else>
          <bar_chart
            v-if="report_template.view_sub_type == 'bar'"
            :chart-data="datacollection"
            :options="bar_chart_options_non_time_series">
          </bar_chart>
        </div>
      </v-container>
    </v-card>

    <v-card v-if="report_template.view_type == 'report.count' "
            elevation="0">
      <v-container>
        <v-chip
          large
          :color="color"
          text-color="white"
        >

          <h2> {{ report.count }} </h2>

        </v-chip>
      </v-container>
    </v-card>


    <!-- Bottom -->

    <v-card v-if="may_edit == true" elevation="0">

      <v-alert type="success"
               v-model="success_loading_existing"
               dismissible>
        Loaded Existing Info
      </v-alert>

      <v-alert type="success"
               v-model="success_saved"
               dismissible>
        Saved
      </v-alert>

      <v-snackbar color="success" v-model="success_run" class="pa-0">
        <div class="d-flex justify-center align-center">
          <p class="ma-0">Report Generated successfully.</p>
          <v-btn class="ma-0" small icon @click="success_run = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </div>
      </v-snackbar>

    </v-card>

    <v_error_multiple :error="error">
    </v_error_multiple>
    <v_error_multiple :error="report_warning" type="warning">
    </v_error_multiple>

  </div>
</template>

<script lang="ts">


/*  Caution, re adding new select controls
 *    expects  @change="has_changes = true"  otherwise won't "save"

 *
 */

import axios from '../../services/customInstance';
import label_select_only from '../label/label_select_only.vue'
import {ReportTemplate} from '../../types/ReportTemplate'
import { Report } from '@/types/Report'
import {getReportTemplate} from '../../services/reportServices.ts'
import {CSVReportFormatter} from './CSVReportFormatter';
import Vue from "vue";
import { Schema } from '@/types/Schema'


const date_selector =
    {
      'display_name': 'Date',
      'name': 'date',
      'icon': 'mdi-calendar',
      'color': 'primary'
    }

const user_selector =
    {
      'display_name': 'User',
      'name': 'user',
      'icon': 'mdi-account-circle',
      'color': 'blue'
    }

const label_selector =
    {
      'display_name': 'Label',
      'name': 'label',
      'icon': 'mdi-format-paint',
      'color': 'pink'
    }

const task_selector =
    {
      'display_name': 'Task',
      'name': 'task',
      'icon': 'mdi-flash-circle',
      'color': 'purple'
    }

const file_selector =
    {
      'display_name': 'File (Frame)',
      'name': 'file',
      'icon': 'mdi-file',
      'color': 'orange'
    }

const task_status_selector =
    {
      'display_name': 'Task Status',
      'name': 'task_status',
      'icon': 'mdi-list-status',
      'color': 'green'
    }

const instance_selector =
    {
      'display_name': 'Instance',
      'name': 'instance',
      'icon': 'mdi-brush',
      'color': 'green'
    }

const time_spent_task_selector =
    {
      'display_name': 'Time Spent On Task',
      'name': 'time_spent_task',
      'icon': 'mdi-clock',
      'color': 'blue',
      'allowed_groupings': [
        task_selector,
      ]
    }

const annotator_performance_selector =
    {
      'display_name': 'Annotators Performance',
      'name': 'annotator_performance',
      'icon': 'mdi-camera-timer',
      'color': 'cyan',
      'allowed_groupings': [
        task_selector,
        instance_selector,
      ]
    }

const instance_selector_with_groupings = structuredClone(instance_selector)
instance_selector_with_groupings['allowed_groupings'] = [
          date_selector,       
          user_selector,
          label_selector,
          task_selector,
          file_selector,
          task_status_selector             
        ]

const file_selector_with_groupings = structuredClone(file_selector)
file_selector_with_groupings['allowed_groupings'] = [
          date_selector,       
          user_selector,
          label_selector,
          task_selector,
          file_selector,
          task_status_selector             
        ]

const task_selector_with_groupings = structuredClone(task_selector)
task_selector_with_groupings['allowed_groupings'] = [
          date_selector,       
          user_selector,
          label_selector,
          task_selector,
          file_selector,
          task_status_selector             
        ]



export default Vue.extend({
    name: 'report',
    components: {
      label_select_only
    },
    props: {
      // Optional, for existing report
      'report_template_id': {
        default: null
      },
      'may_edit': {
        default: true,
        type: Boolean
      }
    },
    data() {
      return {

        success_loading_existing: false,
        success_saved: false,
        success_run: false,

        name: null,

        report: null as Report,

        datacollection: {},
        job_select_this_id: null,

        request_time: null,
        stats: {},
        labels: [],
        member_list: [],
        values_metadata: [],
        values: [],

        report_template: {
          'name': 'My Report',
          'archived': false,
          'item_of_interest': 'instance',
          'period': 'last_30_days',
          'date_period_unit': 'day',
          'label_file_id_list': null,
          'group_by': 'date',
          'second_group_by': null,
          'directory_id_list': null,
          'scope': 'project',
          'view_type': 'chart',
          'diffgram_wide_default': false,
          'task_event_type': 'task_created',
          'id': null,
          'view_sub_type': 'line'
        } as ReportTemplate,

        item_of_interest_list: [
          annotator_performance_selector,
          time_spent_task_selector,
          instance_selector_with_groupings,
          file_selector_with_groupings,
          task_selector_with_groupings
        ],

        period_list: [
          {
            'display_name': 'Last 30 Days',
            'name': 'last_30_days',
            'icon': 'mdi-history',
            'color': 'primary'
          },
          {
            'display_name': 'All',
            'name': 'all',
            'icon': 'mdi-select-all',
            'color': 'primary'
          }
        ],

        date_period_unit_list: ['day', 'month', 'year'],
        group_by_list: ['user', 'project', 'job', 'label', 'date'],

        group_by_list_default: [

        ],

        scope_icon_list: [
          {
            'display_name': 'Project',
            'name': 'project',
            'icon': 'mdi-lightbulb',
            'color': 'blue'
          },
          {
            'display_name': 'Org',
            'name': 'org',
            'icon': 'mdi-domain',
            'color': 'green'
          }
        ],

        view_type_list: [
          {
            'display_name': 'Chart',
            'name': 'chart',
            'icon': 'mdi-finance',
            'color': 'green'
          },
          {
            'display_name': 'Count',
            'name': 'count',
            'icon': 'mdi-numeric',
            'color': 'blue'
          }
        ],

        task_status_filter: [
          {
            'display_name': 'All',
            'name': 'all',
            'icon': 'mdi-select-all',
            'color': 'primary'
          },
          {
            'display_name': 'Tasks Created',
            'name': 'task_created',
            'icon': 'mdi-checkbox-marked-circle-plus-outline',
            'color': 'primary'
          },
          {
            'display_name': 'Tasks Completed',
            'name': 'task_completed',
            'icon': 'mdi-check-circle',
            'color': 'green'
          },
          {
            'display_name': 'Tasks Reviewed Requested',
            'name': 'task_review_start',
            'icon': 'mdi-account-multiple-check-outline',
            'color': 'orange'
          },
          {
            'display_name': 'Tasks Reviewed Approved',
            'name': 'task_review_complete',
            'icon': 'mdi-account-multiple-check-outline',
            'color': 'cyan'
          },
          {
            'display_name': 'Tasks Rejected',
            'name': 'task_request_changes',
            'icon': 'mdi-alert-circle',
            'color': 'red'
          },
        ],
        view_sub_type_list: [
          {
            'display_name': 'Bar',
            'name': 'bar',
            'icon': 'mdi-chart-bar',
            'color': 'green'
          },
          {
            'display_name': 'Line',
            'name': 'line',
            'icon': 'mdi-chart-line',
            'color': 'blue'
          }
        ],

        job: {},

        date: {},
        previous_date: {},

        options: {
          responsive: true,
          grouped: true,
          maintainAspectRatio: false,
          scales: {
            xAxes: [{
              type: 'time',
              distribution: 'series',
              time: {
                unit: 'values_metadataday',
                unitStepSize: 1,
                displayFormats: {
                  'day': 'MMM DD'
                }
              },
            }],

            yAxes: [{
              ticks: {
                beginAtZero: true,
                fixedStepSize: 1
              }
            }]
          }
        },



        bar_chart_options_time_series: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            xAxes: [{
              ticks: {
                beginAtZero: true
              },
              distribution: 'series',
              type: 'time',
              time: {
                unit: 'day',
                unitStepSize: 1,
                displayFormats: {
                  'day': 'MMM DD'
                }
              }
            }],

            yAxes: [{
              ticks: {
                beginAtZero: true
              }
            }]
          }
        },


        bar_chart_options_non_time_series: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            xAxes: [{
              ticks: {
                beginAtZero: true
              }
            }],

            yAxes: [{
              ticks: {
                beginAtZero: true
              }
            }]
          }
        },

        show_filters_dialog: false,

        loading: false,
        error: {},
        report_warning: {},
        result: null,

        auth: {},
        show_auth: false,

        has_changes: false,

        permission_level_list: ['Editor', 'Viewer'],
        permission_level: 'Editor',

      }
    },

    computed: {
      // context of having a "preview" for the report
      // along with a way to save it?

      member_list_label: function () {
        if (this.report_template.item_of_interest === 'task') {
          return 'Assigned To.';
        } else {
          return 'User';
        }
      },

      current_group_by_list: function(){
        let item_of_interest = this.report_template.item_of_interest;
        let ioi_obj = this.item_of_interest_list.find(elm => elm.name === item_of_interest)
        if(ioi_obj){
          return ioi_obj.allowed_groupings;
        }
        else{
          return []
        }

      },

      second_group_by_list: function(){
        // expansion point to limit this more in future
        return [label_selector, user_selector]
      },

      metadata: function () {

        // handle duplicate keys (things that already exist
        // in report_template)
        if (this.job && this.job.id) {   // is clearable (in which case it returns null instead of object)
          this.report_template.job_id = this.job.id
        } else {
          this.report_template.job_id = null
        }

        if (this.report_template.task_id) {
          this.report_template.task_id = parseInt(this.report_template.task_id)
        }

        let dynamic_properties = {
          'date_from': this.date.from,
          'date_to': this.date.to,
          'project_string_id': this.project_string_id,
          'org_id': this.org_id,
          'request_time': this.request_time,
          'member_list': this.member_list

        }
        let result =  {...dynamic_properties, ...this.report_template}

        return result
      },

      // default, maybe in future user can customize

      color: function () {
        return this.item_of_interest_list.find(x => {
          return x.name == this.report_template.item_of_interest
        }).color
      }


    },

    async created() {

      this.project_string_id = this.$store.state.project.current.project_string_id
      this.org_id = this.$store.state.org.current.id

      let result = await this.fetch_report_template()
      if(result){
        this.report_template = result
      }
      if (this.report_template_id != "new") {
        this.run_report(this.report_template_id);

      }

    },
    methods: {
      on_change_item_of_interest: function(new_item){
        let item_of_interest = this.item_of_interest_list.find(elm => elm.name === new_item)
        this.report_template.group_by = item_of_interest.allowed_groupings[0].name;
        //this.reset_second_group_by(item_of_interest)
        this.has_changes = true;
      },

      reset_second_group_by: function (item_of_interest) {
        //this.report_template.second_group_by = null
      },

      set_job: function (job) {
        this.job = job;
        this.has_changes = true
      },

      open_extra_filters_dialog: function () {
        this.show_filters_dialog = true;
      },

      reset_chart_data() {

        this.report = new Report()

        this.fillData(this.report)

      },

      fill_second_group_by(created_datasets, stats, unique_labels){

        if (!stats.second_grouping || stats.second_grouping.length == 0) {
          return created_datasets
        }

        for (let i = 0; i < stats.second_grouping.length; i++) {
          const current = stats.second_grouping[i];
          const label_name = stats.label_names_map[current];
          if (!created_datasets.map(ds => ds.label).includes(label_name)) {
            created_datasets.push({
              label: stats.label_names_map[current],
              backgroundColor: stats.label_colour_map[current].hex,
              data: []
            })
          }
          // Add Value
          //const dataset = created_datasets.find(dset => dset.label === stats.label_names_map[current]);
         // dataset.data[unique_labels.indexOf(stats.labels[i])] = stats.values[i]

        }

        return created_datasets

      },

      warn_if_unique_labels(unique_labels){
        this.report_warning = {};

        if (unique_labels.length > 20) {
          this.datacollection = {}
          this.report_warning['too_many_files'] = 'The report has too many files for complete chart rendering. Showing incomplete data.'
          this.report_warning['csv'] = 'Please download CSV for complete data report.'
          unique_labels = unique_labels.splice(0, 20);
        }
        return unique_labels
      },

      fill_grouped_by_label_chart_data(report) {

        let created_datasets = [];

        let unique_labels = [...new Set(report.labels)];

        unique_labels = this.warn_if_unique_labels(unique_labels)

        this.datacollection = {datasets: [], labels: unique_labels}

        created_datasets = this.fill_second_group_by(created_datasets, stats, unique_labels)

        this.datacollection.datasets = created_datasets
        return created_datasets
      },

      fillData(report) {

        if (this.report_template.second_group_by == 'labels') {
          this.fill_grouped_by_label_chart_data(stats);
        } else {
          this.datacollection = {
            labels: report.labels,
            datasets: [
              {
                // Label that shows on header
                label: stats.header_name ? stats.header_name : this.report_template.item_of_interest,
                data: report.values,
                backgroundColor: this.color
              },

            ]
          }
        }

      },

      save_and_run_report: function () {

        let do_run_report = true

        this.save_report(do_run_report)

      },

      new_report_from_json(report_json) {
        let report = new Report()

        report.count = report_json.count
        report.labels = report_json.labels
        report.values = report_json.values
        report.second_grouping = report_json.second_grouping
        report.values_metadata = report_json.values_metadata

        report.schema = new Schema()
        report.schema.labelColourMap = report_json.label_colour_map
        report.schema.labelNamesMap = report_json.label_names_map

        return report
      },

      update_report_with_user_names(report){

        if (this.report_template.group_by == 'user' || this.report_template.item_of_interest === 'annotator_performance') {
          for (const [i, member_id] of report.labels.entries()) {
            let member = report.values_metadata.find(x => {
              return x.user_id == member_id
            })

            if (member) {
              report.labels[i] = member.first_name + " " + member.last_name
            } else {
              report.labels[i] = "User"
            }

          }
        }

        return report

      },


      load_report: function (report_json) {

        if(!this.report_json){
          return
        }

        this.report = this.new_report_from_json(report_json)

        this.report = this.update_report_with_user_names(this.report)

        if (this.report_template.view_type == "chart") {
          this.fillData(this.report)
        } 

      },

      fetch_report_template: async function(){
        let [report_template, err] = await getReportTemplate(this.project_string_id, this.report_template_id)
        if (err != null){
          console.error(err)
          return
        }
        return report_template

      },

      run_report: function (report_template_id) {

        if (!report_template_id) {
          console.error("Error no report_template_id")
          return
        }

        this.report = null

        this.success_run = false
        this.loading = true
        this.error = {}

        axios.post('/api/v1/report/run', {
          report_template_id: parseInt(report_template_id),
          project_string_id: this.project_string_id 

        }).then(response => {

          this.update_local_data_from_remote_report_template(
            response.data.report_template)

          this.reset_chart_data()

          this.load_report(response.data.report)

          this.success_run = true
          this.loading = false

        })
          .catch(error => {
            this.loading = false
            console.error(error)
            this.error = this.$route_api_errors(error)

          });


      },

      download_csv: function () {

        const csv_formatter = new CSVReportFormatter(this.report)

        let csvContent = csv_formatter.get_csv_data()
        // Inspiration https://stackoverflow.com/questions/14964035/how-to-export-javascript-array-info-to-csv-on-client-side
        var encodedUri = encodeURI(csvContent);
        var link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", `diffgram_report_${this.report_template.id}_${Date.now().toString()}.csv`);
        document.body.appendChild(link); // Required for FF

        link.click(); // This will download the data file
      },

      update_local_data_from_remote_report_template: function (report_template) {

        this.job_select_this_id = report_template.job_id
        // avoid circular updates, since we expect job component to reupdate
        // report template from this id
        this.report_template = {
          ...this.report_template,
          ...report_template
        }

      },

      save_report: function (run_report) {

        if (this.has_changes == false &&
          this.report_template.id != null) {

          if (run_report == true) {
            this.run_report(this.report_template.id)
          }
          return
        }

        this.success_saved = false
        this.loading = true
        this.error = {}
        this.request_time = Date.now()

        axios.post('/api/v1/report/save', {

          metadata: this.metadata,
          report_template_id: this.report_template.id

        }).then(response => {

          this.update_local_data_from_remote_report_template(
            response.data.report_template)

          this.success_saved = true

          if (this.report_template.id != this.report_template_id) {
            this.$router.push('/report/' + this.report_template.id)
          }

          this.has_changes = false

          this.loading = false

          if (run_report == true) {
            this.run_report(this.report_template.id)
          }

        })
          .catch(error => {
            this.loading = false
            this.error = this.$route_api_errors(error)

          });

      }

    }
  }
) </script>
