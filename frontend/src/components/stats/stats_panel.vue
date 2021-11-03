<template>
  <v-container class="grey lighten-5">
    <v-row>
      <v-col v-for="n in 3" :key="n" cols="12" sm="4">
        <v-card class="mx-auto" max-width="100%" outlined>
          <div style="width: 50%">
            <pie-chart :data="chartData" :options="chartOptions"></pie-chart>
          </div>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import Vue from "vue";
import pieChart from "../report/charts/pieChart";
export default Vue.extend({
  components: {
    pieChart,
  },
  data() {
    return {
      chartOptions: {
        hoverBorderWidth: 20,
      },
      chartData: {
        hoverBackgroundColor: "red",
        hoverBorderWidth: 10,
        labels: ["Completed", "In process"],
        datasets: [
          {
            label: "Data One",
            backgroundColor: ["#41B883", "#E46651", "#00D8FF"],
            data: [1, 2],
          },
        ],
      },
    };
  },
});
</script>