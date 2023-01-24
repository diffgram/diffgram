<template>
  <splitpanes @resize="on_panes_resized"
              @ready="$emit('ready')"
              class="default-theme"
              :horizontal="layout_direction === 'horizontal'"
              v-if="root_file.type === 'compound' || root_file.type === 'video' || root_file.type === 'image'"
              :push-other-panes="false" >

    <pane v-for="(item, row_index) in num_rows" :key="`row_${row_index}`">
        <splitpanes  @pane-click="$emit('pane-click', row_index, $event)" @resize="on_panes_resized(row_index, $event)">
            <pane v-for="(col, col_index) in parseInt(num_columns)" :key="`row_${row_index}_col_${col_index}`">
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
    num_columns: {type: Number, required: true},
    layout_direction: {type: String, required: true, default: 'horizontal'},
    root_file: {type: Object, required: true},
  },
  methods: {

    on_panes_resized: function (row_index, panes_dimensions_list){
      this.$emit('panels_resized', row_index, panes_dimensions_list)
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
</style>
