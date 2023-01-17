<template>
  <splitpanes @resize="on_panes_resized"
              class="default-theme" horizontal :push-other-panes="false" style="height: 100%; border: 1px solid red">

    <pane v-for="(row_index, i) in num_rows" :key="`row_${row_index}`">
        <splitpanes>
            <pane v-for="(col_index, j) in parseInt(num_columns)" :key="`row_${row_index}_col_${col_index}`">
              <slot :name="`panel_${row_index}:${col_index}`">
                <div style="width: 400px">
                  <h6 style="font-size: 36px" class="text--black">row: {{row_index}} col {{col_index}}</h6>
                  <v-icon size="46" color="success">mdi-check</v-icon>
                </div>
              </slot>
            </pane>
        </splitpanes>

    </pane>
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
  methods: {

    on_panes_resized: function (panes_dimensions_list){
      this.$emit('panes_resized', panes_dimensions_list)
    }
  }
})
</script>

<style scoped>
.splitpanes__pane {
  display: flex;
  justify-content: center;
  align-items: center;
  font-family: Helvetica, Arial, sans-serif;
  color: rgba(255, 255, 255, 0.6);
  font-size: 5em;
}
</style>
