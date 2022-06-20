<div>
  <bar-chart></bar-chart>
</div>

<script lang="ts">

  import VueCharts from 'vue-chartjs'

  import Vue from "vue"; export default Vue.extend( {
    extends: VueCharts.Bar,
    mixins: [VueCharts.mixins.reactiveProp],
    props: ['options'],
    mounted() {
       // this.chartData is created in the mixin.
      // and then it randomly gets called chart-data as the prop!!
      // seems pretty silly
      this.renderChart(this.chartData, this.options)
    }
  }

) </script>
