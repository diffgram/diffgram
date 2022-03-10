<template>
  <v-card>
    <v-card-title>Annotator Performance</v-card-title>
    <v-card-subtitle>Average time an annotator spends per task.</v-card-subtitle>
    <v-card-text>
      <div>
        <member_select
          v-model="member_list"
          label="Select Users"
          multiple
          :show_names_on_selected="true"
          @change="on_member_list_changed"
          :allow_all_option="true"
          :member_list="$store.state.project.current.member_list"
        ></member_select>
      </div>
      <div>
        <bar_horizontal_chart
          :chart-data="chart_data"
          :options="bar_chart_options_time_series">
        </bar_horizontal_chart>
      </div>
    </v-card-text>
  </v-card>

</template>

<script>
import {runReport} from '../../services/reportServices'
import Bar_horizontal_chart from "@/components/report/charts/bar_horizontal_chart";
export default {
  name: "annotator_performance",
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
      chart_data: {
        datasets: [],
        labels: []
      },
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
    on_member_list_changed: function(member_list){
      console.log('MEMBER LIST', member_list);
      let dataset = this.chart_data.datasets[0];
      let values = [];
      let labels = [];
      for(let i = 0; i < this.report_result.stats.values.length; i++){
        let user_id = this.report_result.stats.labels[i];
        let value = this.report_result.stats.values[i];
        console.log('value', user_id)
        if(member_list.includes(user_id)){
          values.push(value);
          labels.push(`${this.report_result.stats.values_metadata[i].first_name} ${this.report_result.stats.values_metadata[i].last_name}`);
        }
      }
      this.chart_data ={
        labels: labels,
        datasets: [
          {
            backgroundColor: '#757575',
            borderColor: 'white',
            label: 'Average Time Per Task (Mins)',
            data: values
          }
        ]
      }
    },
    gen_report: async function(){
      this.loading = true
      let [result, error] = await runReport(this.project_string_id, undefined, this.report_template)
      if(result){
        console.log('aaa', result)
        this.report_result = result;
        let labels = [];
        for(let i = 0; i< result.stats.labels.length; i++){
          labels.push(`${result.stats.values_metadata[i].first_name} ${result.stats.values_metadata[i].last_name}`);
        }
        this.chart_data ={
          labels: labels,
          datasets: [
            {
              backgroundColor: '#757575',
              borderColor: 'white',
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
