<template>
  <div v-if="editing" class="d-flex" style="width: 100%">
    <div  style="width: 100%" class="d-flex justify-start align-center" >
     <v-btn
       class="mr-1"
       v-for="custom_button in custom_buttons"
       @click="open_button_config(custom_button)"
       x-small
       :color="custom_button.color ? custom_button.color : 'success'">
       {{custom_button.display_name}}
     </v-btn>
    </div>
    <button_edit_context_menu :project_string_id="project_string_id" ref="button_config_menu" :button="current_button"></button_edit_context_menu>
  </div>
  <div v-else class="d-flex" style="width: 100%">
    <div  style="width: 100%" class="d-flex justify-start align-center" >
      <v-btn
        class="mr-1"
        v-for="custom_button in custom_buttons"
        @click="do_button_action(custom_button)"
        x-small :color="custom_button.color ? custom_button.color : 'success'">{{custom_button.display_name}}
      </v-btn>
    </div>
  </div>

</template>

<script lang="ts">

import Vue from 'vue';
import button_edit_context_menu from './button_edit_context_menu.vue'
import {CustomButton} from "../../types/ui_schema/Buttons";
import {CustomButtonWorkflow} from "../../types/ui_schema/CustomButtonWorkflow";
export default Vue.extend({
  name: 'CustomButtonsSection',
  components: {
    button_edit_context_menu,
  },
  props: {
    'ui_schema_prop': {type: Object, required: false},
    'project_string_id': {type: String, required: true},
    'editing': {
      required: true,

    }

  },
  data() {
    // move context menu off the page out of view when hidden
    return {
      current_button: null,
      custom_buttons: [],
    }
  },
  watch:  {
    ui_schema: {
      deep: true,
      handler: function(val){
        if(val && val.custom_buttons){
          const init_buttons = this.initialize_buttons(val.custom_buttons.buttons_list)
          this.custom_buttons = init_buttons;
          this.$forceUpdate()
        }
        if(val && !val.custom_buttons){
          this.custom_buttons = [];
        }
      }
    }
  },
  computed: {
    ui_schema: function(){
      return this.$store.getters.get_current_ui_schema()
    }
  },

  created() {
  },
  mounted() {
    if(this.ui_schema && this.ui_schema .custom_buttons){
      const init_buttons = this.initialize_buttons(this.ui_schema.custom_buttons.buttons_list)
      this.custom_buttons = init_buttons;
      this.$forceUpdate()
    }
    if(this.ui_schema  && !this.ui_schema .custom_buttons){
      this.custom_buttons = [];
    }
  },
  beforeDestroy() {

  },
  methods: {
    initialize_buttons: function(buttons){
      const result = [];
      for(let button of buttons){
        if(button.workflow){
          const workflow = new CustomButtonWorkflow(button.workflow.actions)
          const newButton = new CustomButton({...button, workflow: workflow})
          result.push(newButton)
        } else{
          const newButton = new CustomButton({...button})
          result.push(newButton)
        }


      }
      return result
    },
    do_button_action: function(custom_button){

      if(custom_button && custom_button.workflow){
        console.log('DO ACTION', custom_button)
        this.$emit('execute_button_actions', custom_button)
      }

    },
    open_button_config: function(custom_button: CustomButton){
      this.current_button = custom_button
      this.$refs.button_config_menu.open_menu()
    }
  }
});
</script>

<style>
.context-menu {
  position: absolute;
  margin: 0;
  box-sizing: border-box;
  display: none;
  z-index: 10000;
}

.save-menu {
  position: absolute;
  margin: 0;
  box-sizing: border-box;
  display: none;
  z-index: 1000;
}

.context-menu.visible {
  display: block;
}

.save-menu.visible {
  display: block;
}
</style>
