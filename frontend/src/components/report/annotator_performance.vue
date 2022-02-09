<template>
  <v-card>
    <v-card-title>Annotator Performance</v-card-title>
    <v-card-subtitle>Average Time on Task</v-card-subtitle>
    <v-card-text>
      <div>
        Filters here
      </div>
      <div>
        <bar_chart
          :chart-data="chart_data"
          :options="bar_chart_options_time_series">
        </bar_chart>
      </div>
    </v-card-text>
  </v-card>

</template>

<script>
import {runReport} from '../../services/reportServices'
export default {
  name: "annotator_performance",
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
      chart_data: {
        datasets: [],
        labels: []
      },
      bar_chart_options_time_series: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        legend: {
          position: 'right',
        },
        title: {
          display: true,
          text: 'Chart.js Horizontal Bar Chart'
        },
        scales: {

        }
      },
      report_template: {
        item_of_interest: 'annotator_performance',
        group_by: 'task',
        job_id: null, // Populated on mounted(),
        period: 'all',
        view_type: 'all',
        view_sub_type: 'bar',
      },
      loading: false
    }
  },
  mounted() {
    this.report_template.job_id = this.job_id;
    this.gen_report();
  },
  methods: {
    gen_report: async function(){
      this.loading = true
      let [result, error] = await runReport(this.project_string_id, undefined, this.report_template)
      if(result){
        console.log('aaa', result)
        this.chart_data ={
          labels: result.stats.labels,
          datasets: [
            {
              label: 'Average Time Per Task (Mins)',
              data: result.stats.values
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
