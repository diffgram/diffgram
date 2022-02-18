<template>
  <div>

    <main_menu v-if="may_edit"
               height="210">

      <template slot="second_row">

        <v-toolbar
          style="border-top: 1px solid #e0e0e0"
          dense
          elevation="1"
          fixed
          height="50px"
        >
          <v-toolbar-items>
            <regular_chip
              :message=report_template.id
              tooltip_message="ID"
              color="grey"
              tooltip_direction="bottom"
              :small="true"
            >
            </regular_chip>
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


            <tooltip_button tooltip_message="Save & Refresh Report"
                            @click="save_and_run_report"
                            icon="mdi-refresh"
                            :disabled="loading"
                            :text_style="true"
                            :large="true"
                            color="primary">
            </tooltip_button>

            <tooltip_button tooltip_message="More Filters & Configs"
                            @click="open_extra_filters_dialog"
                            icon="mdi-filter"
                            :disabled="!['instance'].includes(report_template.item_of_interest)"
                            :text_style="true"
                            :large="true"
                            color="primary">
            </tooltip_button>
            <v-dialog v-model="show_filters_dialog"
                      width="800">
              <v-card>
                <v-card-title>More Filters:</v-card-title>
                <v-card-text>
                  <v-container>
                    <h2>Labels & Instances</h2>
                    <v-checkbox @change="has_changes = true" label="Additionally Group Files By Label"
                                v-model="report_template.group_by_labels"></v-checkbox>
                  </v-container>
                </v-card-text>
              </v-card>
            </v-dialog>

            <tooltip_button tooltip_message="Save"
                            @click="save_report"
                            icon="save"
                            :text_style="true"
                            :large="true"
                            :disabled="!has_changes"
                            color="primary">
            </tooltip_button>

            <tooltip_button
              tooltip_message="Back to Report List"
              @click="$router.push('/reports/list')"
              icon="list"
              :icon_style="true"
              :large="true"
              color="primary">
            </tooltip_button>

            <tooltip_button
              tooltip_message="Download as CSV"
              @click="download_csv"
              icon="mdi-download"
              color="primary"
              :disabled="loading"
              :text_style="true"
              :large="true"
            >
            </tooltip_button>

            <div class="pa-2">
              <div v-if="has_changes">
                Changes detected.
              </div>
              <div v-else>
                No changes.
              </div>
            </div>

            <div class="pa-2 pl-4 pr-4">
              <regular_chip
                :message=count
                tooltip_message="Sum"
                color="primary"
                tooltip_direction="bottom">
              </regular_chip>

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
                <!-- SCOPE -->
                <diffgram_select
                  class="pa-4"
                  :item_list="scope_icon_list"
                  v-model="report_template.scope"
                  label="Permission Scope"
                  :disabled="true || loading"
                  @change="has_changes = true"
                >
                </diffgram_select>

              </v-col>
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

            <v-row>
              <v-col cols="3">
                <div style="min-width: 200px" class="pa-4">
                  <job_select v-model="job"
                              :disabled="loading ||
                            !['file', 'task', 'instance'].includes(report_template.item_of_interest)"
                              @change="set_job"
                              :select_this_id="job_select_this_id"
                  >

                  </job_select>
                </div>
              </v-col>
              <v-col cols="3">
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
             v-if="!loading && values.length == 0 && count ==0"
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

    <v-card v-if="report_template.view_type == 'count' "
            elevation="0">
      <v-container>
        <v-chip
          large
          :color="color"
          text-color="white"
        >

          <h2> {{ count }} </h2>

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
 *
 *
 *
 */

import axios from '../../services/customInstance';
import label_select_only from '../label/label_select_only.vue'
import tooltip_button from '../regular/tooltip_button.vue'
import {CSVReportFormatter} from './CSVReportFormatter';
import Vue from "vue";

export default Vue.extend({
    name: 'report',
    components: {
      label_select_only,
      tooltip_button,
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

        datacollection: {},
        job_select_this_id: null,

        request_time: null,
        stats: {},
        labels: [],
        member_list: [],
        values: [],

        /*
         *
         */
        report_template: {
          'name': 'My Report',
          'archived': false,
          'item_of_interest': 'instance',
          'period': 'last_30_days',
          'date_period_unit': 'day',
          'label_file_id_list': null,
          'group_by': 'date',
          'directory_id_list': null,
          'scope': 'project',
          'view_type': 'chart',
          'diffgram_wide_default': false,
          'group_by_labels': false,
          'id': null,
          'view_sub_type': 'line'
        },

        item_of_interest_list: [
          {
            'display_name': 'Annotators Performance',
            'name': 'annotator_performance',
            'icon': 'mdi-camera-timer',
            'color': 'cyan',
            'allowed_groupings': [
              {
                'display_name': 'Task',
                'name': 'task',
                'icon': 'mdi-flash-circle',
                'color': 'purple'
              },
              {
                'display_name': 'Instance',
                'name': 'instance',
                'icon': 'mdi-brush',
                'color': 'green'
              },
            ]
          },
          {
            'display_name': 'Time Spent On Task',
            'name': 'time_spent_task',
            'icon': 'mdi-clock',
            'color': 'blue',
            'allowed_groupings': [
              {
                'display_name': 'Task',
                'name': 'task',
                'icon': 'mdi-flash-circle',
                'color': 'purple'
              },
            ]
          },
          {
            'display_name': 'Instance',
            'name': 'instance',
            'icon': 'mdi-format-paint',
            'color': 'green',
            'allowed_groupings': [
              {
                'display_name': 'Date',
                'name': 'date',
                'icon': 'mdi-calendar',
                'color': 'primary'
              },
              {
                'display_name': 'User',
                'name': 'user',
                'icon': 'mdi-account-circle',
                'color': 'blue'
              },
              {
                'display_name': 'Label',
                'name': 'label',
                'icon': 'mdi-format-paint',
                'color': 'pink'
              },
              {
                'display_name': 'Task',
                'name': 'task',
                'icon': 'mdi-flash-circle',
                'color': 'purple'
              },
              {
                'display_name': 'File (Frame)',
                'name': 'file',
                'icon': 'mdi-file',
                'color': 'orange'
              },
              {
                'display_name': 'Task Status',
                'name': 'task_status',
                'icon': 'mdi-list-status',
                'color': 'green'
              },
            ]
          },
          {
            'display_name': 'File (Frame)',
            'name': 'file',
            'icon': 'mdi-file',
            'color': 'orange',
            'allowed_groupings': [
              {
                'display_name': 'Date',
                'name': 'date',
                'icon': 'mdi-calendar',
                'color': 'primary'
              },
              {
                'display_name': 'User',
                'name': 'user',
                'icon': 'mdi-account-circle',
                'color': 'blue'
              },
              {
                'display_name': 'Label',
                'name': 'label',
                'icon': 'mdi-format-paint',
                'color': 'pink'
              },
              {
                'display_name': 'Task',
                'name': 'task',
                'icon': 'mdi-flash-circle',
                'color': 'purple'
              },
              {
                'display_name': 'File (Frame)',
                'name': 'file',
                'icon': 'mdi-file',
                'color': 'orange'
              },
              {
                'display_name': 'Task Status',
                'name': 'task_status',
                'icon': 'mdi-list-status',
                'color': 'green'
              },
            ]
          },
          {
            'display_name': 'Task',
            'name': 'task',
            'icon': 'mdi-flash-circle',
            'color': 'purple',
            'allowed_groupings': [
              {
                'display_name': 'Date',
                'name': 'date',
                'icon': 'mdi-calendar',
                'color': 'primary'
              },
              {
                'display_name': 'User',
                'name': 'user',
                'icon': 'mdi-account-circle',
                'color': 'blue'
              },
              {
                'display_name': 'Label',
                'name': 'label',
                'icon': 'mdi-format-paint',
                'color': 'pink'
              },
              {
                'display_name': 'Task',
                'name': 'task',
                'icon': 'mdi-flash-circle',
                'color': 'purple'
              },
              {
                'display_name': 'File (Frame)',
                'name': 'file',
                'icon': 'mdi-file',
                'color': 'orange'
              },
              {
                'display_name': 'Task Status',
                'name': 'task_status',
                'icon': 'mdi-list-status',
                'color': 'green'
              },
            ]
          }
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
        //group_by_list: ['user', 'project', 'job', 'label', 'date'],

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
                unit: 'day',
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


        // TODO some more stuff to look at here option wise
        // in terms of having this work with other things like labels

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

        // TODO must be better way to share this??

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

        count: null,

        show_filters_dialog: false,
        label_colour_map: null,
        label_names_map: null,
        second_grouping: null,
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

      /*  Is it worth it to have this as a computed function
       *  instead of editing it directly?
       *
       *  I vaguelly recall somewhere that creating the raw object
       *  from JSON serialized thing sometimes had issues
       *  but perhaps is still cleaner.
       *
       *  Update:
       *    One reason to do it this way, is that
       *    'date' object is a dict, and that makes it difficult
       *    to update from a regular dict.
       *
       *   How we set things here could get dicey very quickly
       *
       *   What if we just had date seperate then added in the keys
       *   Seems like that's a reasonably way to do it
       *   then we can at least set some of the stuff easier from existing
       *
       */

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
        // merge properties
        return {...dynamic_properties, ...this.report_template}
      },

      // default, maybe in future user can customize

      color: function () {
        return this.item_of_interest_list.find(x => {
          return x.name == this.report_template.item_of_interest
        }).color
      }


    },
    mounted() {


    },

    created() {
      // Defaults
      this.project_string_id = this.$store.state.project.current.project_string_id
      this.org_id = this.$store.state.org.current.id

      // TODO only do this in edit mode.

      // TODO implement get_report() using report_template_id if provided.
      // we asume if it's valid then it will update the report object appropriately

      /*
       * Not clear when value of running just get_report() here
       * because we get template info back from runnin the report
       * and in new case it's blank anyway
       */
      // this.get_report(this.report_template_id)

      if (this.report_template_id != "new") {
        this.run_report(this.report_template_id);

      }

    },
    methods: {
      on_change_item_of_interest: function(new_item){
        console.log('ITEM', new_item, this.item_of_interest_list)
        let item_of_interest = this.item_of_interest_list.find(elm => elm.name === new_item)
        console.log('item_of_interest', item_of_interest)
        this.report_template.group_by = item_of_interest.allowed_groupings[0].name;
        this.has_changes = true;
      },
      set_job: function (job) {
        this.job = job;
        this.has_changes = true
      },
      open_extra_filters_dialog: function () {
        this.show_filters_dialog = true;
      },
      reset_chart_data() {
        this.labels = [];
        this.values = [];
        this.second_grouping = [];
        this.label_colour_map = null;
        this.label_names_map = null;
        this.fillData({
          labels: [],
          values: [],
          second_grouping: [],
          label_colour_map: null,
          label_names_map: null,
        })

      },
      fill_grouped_by_label_chart_data(stats) {
        const created_datasets = [];
        this.report_warning = {};
        let unique_labels = [...new Set(stats.labels)];
        if (unique_labels.length > 20) {
          this.datacollection = {}
          this.report_warning['too_many_files'] = 'The report has too many files for complete chart rendering. Showing incomplete data.'
          this.report_warning['csv'] = 'Please download CSV for complete data report.'
          unique_labels = unique_labels.splice(0, 20);
        }
        this.datacollection = {datasets: [], labels: unique_labels}
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
          const dataset = created_datasets.find(dset => dset.label === stats.label_names_map[current]);
          dataset.data[unique_labels.indexOf(stats.labels[i])] = stats.values[i]

        }
        this.datacollection.datasets = created_datasets
        return created_datasets
      },
      fillData(stats) {
        if (this.report_template.group_by_labels) {
          this.fill_grouped_by_label_chart_data(stats);
        } else {
          this.datacollection = {
            labels: stats.labels,
            datasets: [
              {
                // Label that shows on header
                label: stats.header_name ? stats.header_name : this.report_template.item_of_interest,
                data: stats.values,
                backgroundColor: this.color
              },

            ]
          }
        }

      },

      save_and_run_report: function () {
        /*
         *
         *  For now we assume we must have a saved report to run it
         *  as a future optimization can look at more ways to
         *  run this just in "preview" mode...
         *
         */

        let do_run_report = true

        this.save_report(do_run_report)

      },


      load_stats: function (stats) {

        this.stats = stats

        // assumes project scope

        if (this.report_template.group_by == 'user') {
          for (const [i, member_id] of this.stats.labels.entries()) {
            let member = this.$store.state.project.current.member_list.find(x => {
              return x.member_id == member_id
            })

            if (member) {
              this.stats.labels[i] = member.first_name + " " + member.last_name
            } else {
              this.stats.labels[i] = "User"
            }

          }
        }


        if (this.report_template.view_type == "chart") {

          /*
         * assumes stats is a dict
         */

          this.labels = stats.labels
          this.values = stats.values
          this.second_grouping = stats.second_grouping
          this.label_names_map = stats.label_names_map
          this.label_colour_map = stats.label_colour_map
          this.count = stats.count

          this.fillData(stats)
        } else if (this.report_template.view_type == "count") {
          this.count = stats
        }

      },

      run_report: function (report_template_id) {

        if (!report_template_id) {
          console.error("Error no report_template_id")
          return
        }

        this.count = null

        this.success_run = false
        this.loading = true
        this.error = {}

        axios.post('/api/v1/report/run', {
          report_template_id: parseInt(report_template_id),
          project_string_id: this.project_string_id   // for default reports

        }).then(response => {

          // careful need to grab this too to update other report concepts
          // and this should happen before load stats so colors are all good
          this.update_local_data_from_remote_report_template(
            response.data.report_template)
          this.reset_chart_data()
          this.load_stats(response.data.stats)

          this.success_run = true

          this.loading = false

        })
          .catch(error => {
            this.loading = false
            this.error = this.$route_api_errors(error)

          });


      },

      get_report: function (report_template_id) {
        /*
         * TODO consider doing similar style like run where we pass the project_string_id in post
         * so we can do permission check that way.
         *
         */

        // we get this from the url so hard to do null check
        // and still have it look good?
        if (report_template_id == "new") {
          // could also check if it's not a "Number" type or something.
          return
        }

        this.success_loading_existing = false
        this.loading = true
        this.error = {}

        axios.get('/api/v1/report/info/' + report_template_id
        ).then(response => {

          // We do compelte object here
          // because there are things like member_created_id
          // and other stuff that may get "added" from the back end

          this.update_local_data_from_remote_report_template(
            response.data.report_template)

          this.success_loading_existing = true
          this.loading = false

        })
          .catch(error => {
            this.loading = false
            this.error = this.$route_api_errors(error)

          });


      },

      download_csv: function () {


        const csv_formatter = new CSVReportFormatter(
          this.labels,
          this.values,
          this.second_grouping,
          this.label_names_map,
          this.report_template
        )
        let csvContent = csv_formatter.get_csv_data()
        console.log('AAAA', csvContent)
        // Inspiration https://stackoverflow.com/questions/14964035/how-to-export-javascript-array-info-to-csv-on-client-side
        var encodedUri = encodeURI(csvContent);
        var link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", `diffgram_report_${this.report_template.id}_${Date.now().toString()}.csv`);
        document.body.appendChild(link); // Required for FF

        link.click(); // This will download the data file
      },
      update_local_data_from_remote_report_template: function (report_template) {
        /* context of local items using say a dict (like job select)
         * and we may want a concrete report to save it, and update it.
         *
         */
        this.job_select_this_id = report_template.job_id
        // avoid circular updates, since we expect job component to reupdate
        // report template from this id
        this.report_template = report_template

      },

      save_report: function (run_report) {
        /*
          * Assumes saving one report at a time.
          *
          * If we don't have a report id yet we need to save first
          *
          *
          *  TODO load concrete filters like job id
          *
          */

        if (this.has_changes == false &&
          this.report_template.id != null) {

          /*
           *  not a fan of having this here
            but it seemed like easist way
            since for changes we need to run this
            later after save success
           *
           */

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

          // We do compelte object here
          // because there are things like member_created_id
          // and other stuff that may get "added" from the back end

          this.update_local_data_from_remote_report_template(
            response.data.report_template)

          this.success_saved = true

          /*
           * We detect things off of the URL so we want
           * it to be updated when an id is newly created.
           *
           * ie if user refreshes page etc.
           *
           * This updates the "route" to the new id
           *
           * Only for New routes, so if it's already equal just leave it.
           */
          if (this.report_template.id != this.report_template_id) {
            this.$router.push('/report/' + this.report_template.id)
          }

          this.has_changes = false

          this.loading = false

          /*
           * careful running report
           * uses existing saved id
           * so we must have this request complete
           * before we can call it
           *
           * run_report in theory can use same metadata
           * but for now this feels like stronger validation path
           */
          if (run_report == true) {
            this.run_report(this.report_template.id)
          }

        })
          .catch(error => {
            this.loading = false
            this.error = this.$route_api_errors(error)

          });

      },


      stats_task_api: function () {

        this.loading = true
        this.error = {}
        this.result = null

        // temp for testing
        // this.directory_id_list = [this.$store.state.project.current_directory.directory_id]

        axios.post('/api/v1/diffgram/stats/general',
          {
            'date_from': this.date.from,
            'date_to': this.date.to,
            'item_of_interest': this.item_of_interest,
            'date_period_unit': this.date_period_unit,
            'count_only': this.count_only,
            'label_file_id_list': this.label_file_id_list,
            //'group_by': this.group_by,
            'directory_id_list': this.directory_id_list

          }).then(response => {
          let log = response.data.log
          if (log.success == true) {

            this.labels = response.data.stats.labels
            this.values = response.data.stats.values
            this.fillData(response.data.stats)

            this.count = response.data.stats.count

          }
          this.loading = false

        })
          .catch(error => {
            this.loading = false

            this.error = this.$route_api_errors(error)


          });
      }
    }
  }
) </script>
