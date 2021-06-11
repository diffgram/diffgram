<template>
  <div class="d-flex">
    <v-autocomplete
      style="max-width: 350px"
      clearable
      :multiple="multi_select"
      :items="model_run_list"
      return-object
      v-model="current_run"
      label="Select Model Run"
      @change="model_run_change"
      :item-text="getFieldText"
      :item-value="'id'"
    >
      <template v-slot:selection="data">
        <v-chip class="d-flex align-content-start justify-start pa-2">
          {{ data.item.reference_id }}
          <div v-if="!multi_select" class="ma-2" :style="{background: selected_color, width: '20px', height: '20px', borderRadius: '5px'}"></div>
          <div v-else class="ma-2" :style="{background: color_list[data.index], width: '20px', height: '20px', borderRadius: '5px'}"></div>
        </v-chip>
      </template>
    </v-autocomplete>

  </div>
</template>

<script>
  import Vue from "vue";
  import {model_run_colors} from "./model_run_colors";

  export default Vue.extend( {
    name: "model_run_selector",
    props:{
      project_string_id:{
        default: null
      },
      multi_select: {
        default: false
      },
      model_run_list: {
        default: false
      },
      selected_color: {
        default: 'lime'
      }
    },
    data: function(){
      return{
        current_run: undefined,
        color_list: model_run_colors
      }
    },
    computed:{
      num_selected: function(){
        if(Array.isArray(this.current_run)){
          return this.current_run.length
        }
        return 0
      }
    },
    methods:{
      getFieldText: function(item){
        return item.reference_id;
      },
      model_run_change: function(item){
        if(this.$props.multi_select){
          let final_val = item;
          let index = 0;
          for(const elm of final_val){
            elm.color = this.color_list[index]
            index += 1;
          }
          this.$emit('model_run_change', final_val);
        }
        else{
          if(!item){
            this.$emit('model_run_change', item);
            return
          }
          let final_val = {...item}
          final_val.color = this.$props.selected_color;
          this.$emit('model_run_change', final_val);
        }

      }
    }
  })
</script>

<style scoped>

</style>
