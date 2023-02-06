<template>
  <v-card
    flat
    tile
  >
    <v-card-title>Grid Controls</v-card-title>
    <v-card-text>
      <v-text-field
        v-model="rows"
        hint="Rows:"
        label="Rows:"
        type="number"
        @change="on_change_rows"
      />
      <v-text-field
        v-model="cols"
        hint="Columns:"
        label="Columns:"
        type="number"
        @change="on_change_cols"
      />
    </v-card-text>
  </v-card>
</template>

<script class="ts">
// In your Vue component.
import Vue from 'vue'
import { Splitpanes, Pane } from 'splitpanes'
import 'splitpanes/dist/splitpanes.css'
export default Vue.extend({
  name: "panel_manager_toolbar",
  props: {
    initial_cols: {type: Number},
    initial_rows: {type: Number}
  },
  mounted() {
    this.rows = this.initial_rows
    this.cols = this.initial_cols
  },
  watch:{
    initial_cols: function(newVal){
      this.cols = parseInt(newVal, 10)
      this.$emit('change_cols', this.cols)
    },
    initial_rows: function(newVal){
      this.row = parseInt(newVal, 10)
      this.$emit('change_rows', this.rows)
    }
  },
  data: function (){
    return{
        cols:0,
        rows:0,
    }
  },
  methods: {
    on_change_rows: function(rows){
      this.rows = parseInt(rows, 10)
      this.$emit('change_rows', this.rows)
      this.$forceUpdate()
    },
    on_change_cols: function (cols){
      this.cols = parseInt(cols, 10)
      this.$emit('change_cols', this.cols)
      this.$forceUpdate()
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
.toolbar{
  position: absolute;
  top: 0;
  right: 0;
  z-index: 99;
}
.splitpanes-container{
  height: 100%;
}
</style>
