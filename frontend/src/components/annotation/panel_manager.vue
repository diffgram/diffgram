<template>
  <div
    v-if="multipane_supported_file"
    class="splitpanes-container"
  >
    <panel_manager_toolbar
      v-if="root_file.type === 'compound' && root_file.subtype !== 'conversational'"
      :panel_settings="panel_settings" class="toolbar"
      @grid_changed="$emit('grid_changed')"
    />
    <splitpanes
      class="default-theme"
      style="width: 100%"
      :horizontal="layout_direction === 'horizontal'"
      :push-other-panes="false"
      @resize="on_rows_resized"
      @ready="$emit('ready')"
    >
      <pane
        v-for="(item, row_index) in num_rows" :key="`row_${row_index}`"
        :style="{height: child_annotation_ctx_list[row_index] ? `${child_annotation_ctx_list[row_index].container_height}px` : undefined }"
      >
        <splitpanes
          @pane-click="$emit('pane-click', row_index, $event)"
          @resize="on_col_resized(row_index, $event)"
        >
          <pane
            v-for="(col, col_index) in parseInt(num_columns)"
            :key="`row_${row_index}_col_${col_index}`"
            :style="`align-items: ${get_file_type(row_index, col_index) == 'text' ? 'flex-start' : 'center'}; overflow-y: auto;`"
            :class="{'pane-container-unselected': selected_row !== row_index || selected_col !== col_index, 'pane-container': true}"
          >
            <slot :name="`panel_${row_index}:${col_index}`">
              <div style="width: 400px">
                <h6
                  style="font-size: 36px"
                  class="text--black"
                >
                  row: {{row_index}} col {{col_index}}
                </h6>
              </div>
            </slot>
          </pane>
        </splitpanes>
      </pane>
    </splitpanes>
  </div>
  <div v-else>
    <slot :name="`panel_${0}:${0}`" />
  </div>
</template>

<script>
// In your Vue component.
import Vue from 'vue'
import { Splitpanes, Pane } from 'splitpanes'
import panel_manager_toolbar from "@/components/annotation/panel_manager_toolbar.vue";
import 'splitpanes/dist/splitpanes.css'

export default Vue.extend({
  name: "panel_manager",
  components: {
    Splitpanes,
    Pane,
    panel_manager_toolbar
  },
  props: {
    num_rows: {
      type: Number,
      required: true
    },
    selected_row: {
      type: Number
    },
    selected_col: {
      type: Number
    },
    num_columns: {
      type: Number,
      required: true
    },
    layout_direction: {
      type: String,
      default: 'horizontal'
    },
    root_file: {
      type: Object,
      required: true
    },
    panel_settings: {
      type: Object,
      required: true
    },
    working_file_list: {
      type: Array,
      default: []
    },
    child_annotation_ctx_list: {
      type: Array,
      default: []
    },
  },
  mounted() {
    this.disable_resize(this.root_file)
    if(!this.multipane_supported_file){
      this.$emit('ready')
    }
  },
  watch: {
    root_file: {
      deep: true,
      handler: function(newVal) {
        this.disable_resize(newVal)

      }
    }
  },
  computed: {
    multipane_supported_file: function(){
      return this.root_file.type === 'compound' || this.root_file.type === 'video' || this.root_file.type === 'image'
    }
  },
  methods: {
    on_col_resized: function (row_index, panes_dimensions_list){
      this.$emit('cols_resized', row_index, panes_dimensions_list)
    },
    on_rows_resized: function (panes_dimensions_list){
      this.$emit('rows_resized', panes_dimensions_list)
    },
    get_file_type: function(row, col) {
      const file_type = this.working_file_list.find(file => file.row === row && file.column === col)

      if (!file_type) return null
      return file_type.type
    },
    disable_resize: function(file) {
      const list = document.getElementsByClassName("splitpanes__splitter")
      if (file.subtype === 'conversational') {
        for (let item of list) {
          item.classList.add("noClick")
        }
      } else {
        const list = document.getElementsByClassName("splitpanes__splitter")
        for (let item of list) {
          item.classList.remove("noClick")
        }
      }
    }
  }
})
</script>

<style>

.splitpanes__pane {
  display: flex;
  justify-content: center;
  align-items: center;

  overflow: visible;

  color: rgba(255, 255, 255, 0.6);
}
/* .splitpanes--vertical > .splitpanes__splitter {
  min-width: 6px;
  background: linear-gradient(90deg, #ccc, #111) !important;
}

.splitpanes--horizontal > .splitpanes__splitter {
  min-height: 6px;
  background: linear-gradient(0deg, #ccc, #111) !important;
} */

.noClick {
  pointer-events: none !important
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
.splitpanes-container{
  height: 100%;
  position: relative;
}
.toolbar{
  position: absolute;
}
</style>
