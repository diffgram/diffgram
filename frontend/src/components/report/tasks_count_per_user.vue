<template>
  <v-card style="position: relative">
    <standard_button tooltip_message="Save & Refresh Report"
                     @click="gen_report"
                     style="position: absolute; right: 0; top: 0"
                     icon="mdi-refresh"
                     :text_style="true"
                     :large="false"
                     color="primary">
    </standard_button>
    <v-card-title>Tasks Per User</v-card-title>
    <v-card-subtitle class="d-flex align-content-lg-space-between justify-space-between">
      <span>Actions over tasks per user</span>
    <span>
      Total Actions Count:
            <v-chip color="secondary" small>{{count_sum}}</v-chip>
    </span>
    </v-card-subtitle>

    <v-card-text>
      <div>
        <diffgram_select
          v-if="['task'].includes(report_template.item_of_interest)"
          class="pa-4"
          :item_list="task_status_filter"
          v-model="report_template.task_event_type"
          label="Task Status"
          @change="on_task_status_changed"
        >
        </diffgram_select>
      </div>
      <div v-if="!no_data">
        <bar_horizontal_chart
          :chart-data="chart_data"
          :options="bar_chart_options_time_series">
        </bar_horizontal_chart>
      </div>
      <div v-else>
        <p>No data</p>
      </div>
    </v-card-text>
  </v-card>

</template>

<script lang="ts">
import {runReport} from '../../services/reportServices.ts'
import Bar_horizontal_chart from "../report/charts/bar_horizontal_chart";
export default {
  name: "tasks_count_per_user",
  components: {Bar_horizontal_chart},
  props: {
    job_id: {
      default: null
    },
    project_string_id: {
      default: null
    }
  },
  data: function(){
    return {
      member_list: [],
      report_result: [],
      count_sum: 0,
      no_data: false,

      chart_data: {
        datasets: [],
        labels: []
      },
      task_status_filter: [
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
      bar_chart_options_time_series: {
        responsive: true,
        maintainAspectRatio: true,
        elements: {
          bar: {
            borderWidth: 2,
          }
        },
        plugins:{
          legend: {
            position: 'right',
          },
          title: {
            display: true,
            text: 'Chart.js Horizontal Bar Chart'
          },
        },
        scales:{
          xAxes: [{
            ticks: {
              beginAtZero: true
            },
          }],
        }
      },
      report_template: {
        item_of_interest: 'task',
        group_by: 'user',
        job_id: null, // Populated on mounted(),
        period: 'all',
        scope: 'project',
        view_type: 'chart',
        date_period_unit: 'day',
        view_sub_type: 'bar',
        task_event_type: 'task_completed'
      },
      loading: false
    }
  },
  mounted() {
    this.report_template.job_id = this.job_id;

    this.gen_report();
  },
  methods: {
    on_task_status_changed: function(status){
      this.gen_report();
    },
    gen_report: async function(){
      this.loading = true
      let [result, error] = await runReport(this.project_string_id, undefined, this.report_template)
      if(result && result.stats){
        this.report_result = result;
        let labels = [];
        labels = result.stats.labels

        this.count_sum = result.stats.values.reduce((acc, current) => acc + current, 0)
        this.no_data = false
        this.chart_data ={
          labels: labels,
          datasets: [
            {
              backgroundColor: this.task_status_filter.find(elm => elm.name === this.report_template.task_event_type).color,
              borderColor: 'white',
              label: this.task_status_filter.find(elm => elm.name === this.report_template.task_event_type).display_name,
              data: result.stats.values
            }
          ]
        }
      } else {
        this.no_data = true
        this.count_sum = 0
        this.chart_data ={
          datasets: [
            {
              data: []
            }
          ]
        }
      }
    }
  }
}
</script>

<style scoped>

</style>
