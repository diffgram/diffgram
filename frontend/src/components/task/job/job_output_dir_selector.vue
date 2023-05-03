<template>
  <v-container class="ma-0">
    <v-row>
      <v-col cols="12" class="d-flex flex-column">
        <v-radio-group v-model="output_dir_action" :mandatory="true" @change="on_option_change">
          <v-radio label="Move the files to a Dataset" value="move"></v-radio>

          <global_dataset_selector
            ref="dir_list_move"
            :show_new="true"
            :initial_dir_from_state="false"
            :update_from_state="false"
            :set_current_dir_on_change="false"
            :show_update="true"
            :view_only_mode="output_dir_action !== 'move'"
            :set_from_id="move_id"
            @change_directory="on_change_move_dir"
          />

          <v-radio label="Copy the files to a Dataset" value="copy"></v-radio>

          <global_dataset_selector
            ref="dir_list_copy"
            :set_from_id="copy_id"
            :show_new="true"
            :initial_dir_from_state="false"
            :update_from_state="false"
            :set_current_dir_on_change="false"
            :view_only_mode="output_dir_action !== 'copy'"
            :show_update="true"
            @change_directory="on_change_copy_dir"
          />

          <v-radio label="Do nothing." :value="'nothing'"></v-radio>
        </v-radio-group>
      </v-col>
    </v-row>

  </v-container>

</template>

<script lang="ts">
  import Vue from "vue";
  import global_dataset_selector from "../../attached/global_dataset_selector.vue"

  export default Vue.extend({
      name: 'job_output_dir_selector',
      model: {
        prop: 'job',
        event: 'change'
      },
      props: {
        'job': {
          default: undefined,
          type: Object
        },
        'project_string_id': {
          default: undefined,
          type: String
        },
      },
      components: {
        global_dataset_selector
      },
      computed:{
        move_id: function(){
          if(this.move_dir){
            return this.move_dir.directory_id
          }
          return undefined;
        },
        copy_id: function(){
          if(this.copy_dir){
            return this.copy_dir.directory_id
          }
          return undefined;
        }
      },
      data() {
        return {
          attached_dirs: [],
          output_dir_action: 'nothing',
          copy_dir: null,
          move_dir: null,
        }
      },
      created() {
        this.output_dir_action = this.job.output_dir_action ? this.job.output_dir_action : 'nothing';
        if (this.output_dir_action === 'copy') {
          this.copy_dir = this.$store.state.project.current.directory_list.filter(x => x.directory_id === this.job.completion_directory_id)[0]
        } else if (this.output_dir_action === 'move') {
          this.move_dir = this.$store.state.project.current.directory_list.filter(x => x.directory_id === this.job.completion_directory_id)[0]
        }
        this.$emit('output_dir_actions_update', {directory: null, action: this.output_dir_action})
      },

      methods: {
        on_change_copy_dir: function (item) {
          this.copy_dir = item
          if(this.output_dir_action !== 'nothing'){
            this.job.completion_directory_id = item.directory_id;
            this.$emit('output_dir_actions_update', {directory: item, action: this.output_dir_action})
          }
        },
        on_change_move_dir: function (item) {
          this.move_dir = item
          if(this.output_dir_action !== 'nothing'){
            this.job.completion_directory_id = item.directory_id;
            this.$emit('output_dir_actions_update', {directory: item, action: this.output_dir_action})
          }
        },
        on_option_change: function (item) {
          this.job.output_dir_action = item;
          if (item === 'copy') {
            if(this.copy_dir){
              this.job.completion_directory_id = this.copy_dir.directory_id;
            }
            this.$emit('output_dir_actions_update', {directory: this.copy_dir, action: item})
          }
          if (item === 'move') {
            if(this.move_dir){
              this.job.completion_directory_id = this.move_dir.directory_id;
            }
            this.$emit('output_dir_actions_update', {directory: this.move_dir, action: item})
          }
          if (item === 'nothing') {
            this.job.completion_directory_id = undefined;
            this.$refs.dir_list_copy.on_change_dataset()
            this.$refs.dir_list_move.on_change_dataset()
            this.$emit('output_dir_actions_update', {directory: null, action: item})
          }
        }
      }
    }
  ) </script>
