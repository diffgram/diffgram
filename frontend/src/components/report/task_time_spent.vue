<template>
  <v-card>
    <v-card-title>Time Spent On Task</v-card-title>
    <v-card-subtitle>Click on bar to go to task</v-card-subtitle>
    <v-card-text>
      <div>

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
  data: function () {
    return {
      chart_data: {
        datasets: [],
        labels: []
      },
      bar_chart_options_time_series: {
        onClick: this.handleClick,
        onHover: (event, activeElements) => {
          if (activeElements?.length > 0) {
            event.target.style.cursor = 'pointer';
          } else {
            event.target.style.cursor = 'auto';
          }
        },
        responsive: true,
        maintainAspectRatio: false,
        elements: {
          bar: {
            borderWidth: 2,
          }
        },
        plugins: {
          legend: {
            position: 'right',
          },
          title: {
            display: true,
            text: 'Chart.js Horizontal Bar Chart'
          },
        },
        scales: {
          xAxes: [{
            ticks: {
              beginAtZero: true
            },
          }],
        }
      },
      report_template: {
        item_of_interest: 'time_spent_task',
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
    handleClick: function (point, chart_items) {
      if (chart_items.length) {
        let task_id = chart_items[0]._view.label;
        let routeData = this.$router.resolve({name: 'routeName', query: {data: "someData"}});
        window.open(`/task/${task_id}`, '_blank');
        // this.$router.push(`/task/${task_id}`);
      }

    },
    gen_report: async function () {
      this.loading = true
      let [result, error] = await runReport(this.project_string_id, undefined, this.report_template)
      if (result) {

        this.chart_data = {
          labels: result.stats.labels,
          datasets: [
            {
              backgroundColor: 'blue',
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
