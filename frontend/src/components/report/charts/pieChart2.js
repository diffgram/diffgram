import { Pie, mixins } from "vue-chartjs";
export default {
  extends: Pie,
  props: ["data", "options"],
  mounted() {
    // this.chartData is created in the mixin.
    // If you want to pass options please create a local options object
    console.log("DATAA PUE", this.data)
    this.renderChart(this.data, {
      borderWidth: "10px",
      hoverBackgroundColor: "red",
      hoverBorderWidth: "10px",
      radius: '30px',
      ... this.options
    });
  }
};
