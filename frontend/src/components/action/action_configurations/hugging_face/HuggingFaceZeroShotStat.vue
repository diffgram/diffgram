<template>
  <div v-if="!loading" class="chart-wrapper">
      <h3>
          Total action runs: {{ action_list.length }}
      </h3>
      <pie-chart
        :data="run_stats.chartData"
        :options="run_stats.chartOptions"
    />
  </div>
</template>

<script>
import {get_action_run_list, get_action_stat} from '../../../../services/actionService'
import pieChart from "../../../report/charts/pieChart";

export default {
  name: "hf_zero_shot_report",
  components: {
      pieChart
  },
  props: {
    action:{
      required: true,
    },
    project_string_id: {
      required: true
    },
  },
  data (){
    return {
        loading: false,
        action_list: [],
        run_stats: {
            chartOptions: {
                hoverBorderWidth: 20,
                tooltips: {
                    enabled: false,
                },
            },
            chartData: {
                hoverBackgroundColor: "red",
                hoverBorderWidth: 10,
                labels: [],
                datasets: [
                    {
                    label: "Data One",
                    backgroundColor: ["#6ab04c", "#ffbe76", '#7ed6df', '#eb4d4b', '#95afc0'],
                    data: [],
                    },
                ],
            },
        },
    }
  },
  async mounted() {
        this.loading = true;
        const action_run_list = await get_action_run_list(this.project_string_id, this.action.id)
        this.action_list = action_run_list.filter(action_run => action_run.output)
        const labels = {}
        this.action_list.map(action_run => {
            if (!labels[action_run.output.applied_option_label]) {
                labels[action_run.output.applied_option_label] = 1
            } else {
                labels[action_run.output.applied_option_label] += 1
            }
        })
        const label_keys = Object.keys(labels)
        label_keys.map(key => {
            this.run_stats.chartData.datasets[0].data.push(labels[key])
            this.run_stats.chartData.labels.push(`${key} (${labels[key]})`)
        })
        this.loading = false
  },
  methods: {}
}
</script>

<style scoped>
.chart-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center
}
</style>

