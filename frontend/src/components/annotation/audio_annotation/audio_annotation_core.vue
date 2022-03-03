<template>
<div>
  <div style="position: relative">
    <main_menu
      :height="`${!task ? '100px' : '50px'}`"
      :show_default_navigation="!task"
    >
      <template slot="second_row">
        <audio_toolbar
          :has_changed="has_changed"
          :save_loading="save_loading"
          :loading="loading"
          :project_string_id="project_string_id"
          :label_list="label_list"
          :label_file_colour_map="label_file_colour_map"
          :task="task"
          :file="file"
          @on_task_annotation_complete_and_save="on_task_annotation_complete_and_save"
          @task_update_toggle_deferred="defer_task"
          @change_label_file="change_label_file"
          @change_label_visibility="change_label_visibility"
          @change_file="change_file"
          @save="save"
          @change_task="trigger_task_change"
        />
      </template>
    </main_menu>
  </div>
</div>
</template>

<script>
import audio_toolbar from './audio_toolbar'
export default {
  name: "audio_annotation_core",
  components:{
    audio_toolbar
  },
  props: {
    project_string_id:{
      default: null
    },
    task: {
      default: null
    },
    file: {
      default: null
    },
  },
  data: function(){
    return{
      has_changed: false,
      label_list: [],
      label_file_colour_map: {},
      loading: false,
      save_loading: false,
    }
  },
  methods: {
    defer_task: function(){

    },
    change_label_file: function(){

    },
    change_label_visibility: function(){

    },
    change_file: function(){

    },
    save: function(){

    },
    trigger_task_change: function(){

    },
    on_task_annotation_complete_and_save: function(){

    }
  }
}
</script>

<style scoped>

</style>
