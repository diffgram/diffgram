<template>
  <splitpanes @resize="on_rows_resized"
              @ready="$emit('ready')"
              class="default-theme"
              style="width: 100%"
              :horizontal="layout_direction === 'horizontal'"
              v-if="root_file.type === 'compound' || root_file.type === 'video' || root_file.type === 'image'"
              :push-other-panes="false" >

    <pane v-for="(item, row_index) in num_rows" :key="`row_${row_index}`">
        <splitpanes  @pane-click="$emit('pane-click', row_index, $event)" @resize="on_col_resized(row_index, $event)">
            <pane v-for="(col, col_index) in parseInt(num_columns)"
                  :key="`row_${row_index}_col_${col_index}`"
                  :class="{'pane-container-unselected': selected_row !== row_index || selected_col !== col_index, 'pane-container': true}">

              <slot :name="`panel_${row_index}:${col_index}`">
                <div style="width: 400px">
                  <h6 style="font-size: 36px" class="text--black">row: {{row_index}} col {{col_index}}</h6>
                </div>
              </slot>
            </pane>
        </splitpanes>

    </pane>
  </splitpanes>
  <div v-else>
    <slot :name="`panel_${0}:${0}`">

    </slot>
  </div>
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
    selected_row: {type: Number},
    selected_col: {type: Number},
    num_columns: {type: Number, required: true},
    layout_direction: {type: String, required: true, default: 'horizontal'},
    root_file: {type: Object, required: true},
  },
  methods: {

    on_col_resized: function (row_index, panes_dimensions_list){
      this.$emit('cols_resized', row_index, panes_dimensions_list)
    },
    on_rows_resized: function (panes_dimensions_list){
      this.$emit('rows_resized', panes_dimensions_list)
    }
  }
})
</script>

<style scoped>
.splitpanes {

}
.splitpanes__pane {
  display: flex;
  justify-content: center;
  align-items: center;

  color: rgba(255, 255, 255, 0.6);
}
.splitpanes--vertical > .splitpanes__splitter {
  min-width: 6px;
  background: linear-gradient(90deg, #ccc, #111) !important;
}

.splitpanes--horizontal > .splitpanes__splitter {
  min-height: 6px;
  background: linear-gradient(0deg, #ccc, #111) !important;
}
.pane-container-unselected:hover{
  transition: .3s ease;
  box-shadow: 0 0 0 6px #b0b0b0;
  opacity: 0.8;
  cursor: pointer;
}
.pane-container{
  position: relative;
}
</style>
