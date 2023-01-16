<template>
  <splitpanes class="default-theme">
    <splitpanes v-for="row_index in num_rows" :key="`row_${row_index}`">
      <pane v-for="column_index in num_columns" :key="`col_${column_index}`">
        <slot :name="`panel_${row_index}:${column_index}`"/>
      </pane>
    </splitpanes>
  </splitpanes>
</template>

<script>
// In your Vue component.
import Vue from 'vue'
import { Splitpanes, Pane } from 'splitpanes'
import 'splitpanes/dist/splitpanes.css'
export default Vue.extend({
  name: "panel_manager",
  components: { Splitpanes, Pane },
  props: {
    num_rows: {type: Number, required: true},
    num_columns: {type: Number, required: true},
  },
  computed: function (){

  }

})
</script>

<style scoped>

</style>
