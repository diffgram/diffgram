<div style="max-width: 100%">
  <bar-chart :width="width" :height="height"></bar-chart>
</div>

<script lang="ts">

  import VueCharts from 'vue-chartjs'

  import Vue from "vue"; export default Vue.extend( {
    extends: VueCharts.HorizontalBar,
    mixins: [VueCharts.mixins.reactiveProp],
    props: ['options', 'width', 'height'],
    mounted() {
       // this.chartData is created in the mixin.
      // and then it randomly gets called chart-data as the prop!!
      // seems pretty silly
      if(this.width || this.height){
        this.options.maintainAspectRatio = false;
      }
      this.renderChart(this.chartData, this.options)
    }
  }

) </script>
