<template>
  <v-card dense class="pa-0">
   <v-card-text class="d-flex justify-center align-center pa-0" >
     <button_with_menu
       tooltip_message="Grid Settings"
       icon="mdi-grid"
       color="primary"
       small
     >

       <template slot="content">

         <panel_manager_width_height_controls
          :initial_rows="panel_settings.rows"
          :initial_cols="panel_settings.columns"
          @change_rows="on_change_rows"
          @change_cols="on_change_columns"
         ></panel_manager_width_height_controls>
       </template>

     </button_with_menu>
   </v-card-text>

    <!--      <v-btn icon small>-->
    <!--        <v-icon small>mdi-grid-large</v-icon>-->
    <!--      </v-btn>-->
  </v-card>
</template>

<script lang="ts">
// In your Vue component.
import Vue from 'vue'
import { Splitpanes, Pane } from 'splitpanes'
import 'splitpanes/dist/splitpanes.css'
import {PanelsSettings} from "../../types/attributes/PanelsSettings";
import panel_manager_width_height_controls from "@/components/annotation/panel_manager_width_height_controls.vue";
import {ThisTypedComponentOptionsWithArrayProps} from "vue/types/options";
export default Vue.extend({
  name: "panel_manager_toolbar",
  components:{
    panel_manager_width_height_controls: panel_manager_width_height_controls as ThisTypedComponentOptionsWithArrayProps<Vue, any, any, any, any>
  },
  props: {
    panel_settings: {type: Object as PanelsSettings}
  },
  methods:{
    on_change_rows: function(rows){
      console.log('CHANGEEE rows', rows)
      this.panel_settings.rows = rows
      this.$emit('grid_changed')
    },

    on_change_columns: function(cols){
      console.log('CHANGEEE cols', cols)
      this.panel_settings.columns = cols
      this.$emit('grid_changed')
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
