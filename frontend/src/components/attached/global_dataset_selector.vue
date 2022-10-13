<template>
    <dataset_selector
        :project_string_id="$store.state.project.project_string_id"
        :dataset_list="$store.state.project.current.directory_list"
        :set_from_id="set_from_id"
        :clearable="clearable"
        :directory_blacklist="directory_blacklist"
        :view_only_mode="view_only_mode"
        :multiple="multiple"
        :show_new="show_new"
        :show_update="show_update"
        :label="label"
        :change_on_mount="change_on_mount"
        @change_dataset="on_change_dataset"
        @on_set_current_directory="on_set_current_directory"
        @on_refresh_dataset_list="on_refresh_dataset_list"
        @on_focus="on_focus"
        @on_blur="on_blur"
    />
</template>

<script lang="ts">
import Vue from "vue";
import dataset_selector from "../concrete/dataset/dataset_selector.vue"
import axios from '../../services/customInstance';

export default Vue.extend({
  name: 'global_dataset_selector',
  props: {
    'clearable': {
      default: null
    },
    'directory_blacklist': {
      default: undefined
    },
    'initial_dir_from_state': {
      default: true
    },
    'set_current_dir_on_change': {
      default: true,
    },
    'change_on_mount': {
      default: true,
    },
    'view_only_mode': {
      default: false
    },
    'multiple': {
      default: false
    },
    'show_text_buttons':{
      default: false
    },
    'update_from_state': {
      default: true
    },
    'show_new': {
      default: false
    },
    'show_update': {
      default: false
    },
    'set_from_id': {
      default: null,
      type: Number
    },
    'label': {
      default: "Dataset",
      type: String
    }
  },
  components: {
    dataset_selector
  },
  data() {
    return {
      new_directory_menu: false,
      update_directory_menu: false,
      current_directory: {},

      nickname: null,

      date: undefined,
      error_directory_list: {},
      internal_directory_list: undefined,
      loading_directory_list: false

    }
  },
  mounted() {
    this.create_patch_watcher()
    this.create_current_dir_watcher()

  },
  methods: {
    // REFACTORES
    on_change_dataset: function(dataset: object): void {
        this.on_set_current_directory(dataset)
        this.$emit('change_directory', dataset)
    },
    on_set_current_directory: function(dataset: object): void {
        this.$store.commit('set_current_directory', dataset)
    },
    on_refresh_dataset_list: function(dataset_list: Array<any>): void {
        if (dataset_list === this.$store.state.project.current.directory_list) return
        for (let dataset of dataset_list) {
            const directory_in_existing = this.$store.state.project.current.directory_list.find(
                (store_dataset: any) => store_dataset.directory_id === dataset.id
            )

            if (!directory_in_existing) {
                this.$store.commit('patch_single_directory', dataset)
            }
        }
    },
    on_focus: function() {
        this.$store.commit('set_user_is_typing_or_menu_open', true)
    },
    on_blur: function() {
        this.$store.commit('set_user_is_typing_or_menu_open', false)
    },
    create_patch_watcher(): void {
      // if another components patches a dir, eg template context multiple components
      // seperate from current, as someone may switch, does not imply a patch is needed
      // may wish to think about a better "matching" concept here...
      this.patch_dir_watcher = this.$store.watch(
        () => this.$store.state.project.current.last_patched_directory,
        (new_val: any) => {this.patch(new_val)}
      )
    },
    patch(new_directory: any): void {
      // it seems like because of timing we need the splice still?
      let directory_in_existing = this.internal_directory_list.find(
        x => {return x.id === new_directory.id});

      if (!directory_in_existing) {
        this.internal_directory_list.splice(0, 0, new_directory)
      }
    },
    create_current_dir_watcher() {
      /* Why:
       *    When it changes after mount ie in case of {first login + first load} to studio
       *    feels nicer to watch it, rather then just set a timeout and hope it makes it
       *
       * Comment on stronger "project change" concept.
       *    in that case, this may not be needed, however it is nice for super admins / support
       *    where we may be jumping between projects.
       *
       * TODOS
       *   Support multiple directories more smoothly -> https://diffgram.teamwork.com/#/tasks/20232123
       *
       *  May see multiple console logs here becuase multiple components on screen
       *
       */

      this.current_dir_watcher = this.$store.watch(
        () =>  this.$store.state.project.current_directory,   // we assume this the key 'current_directory' will exist here
        (new_val: any) => {
          // No update required case:
          if (
                !new_val || 
                !this.current_directory ||
                new_val.directories_by_id === this.current_directory.directories_by_id
            ) return
          
          // Update required case:
          this.current_directory = new_val
          if (this.$props.update_from_state) {
            this.on_change_dataset()
          }

        }
      )

    }

  },
  beforeDestroy() {
    this.current_dir_watcher()
    this.patch_dir_watcher()
  }
})
</script>


<style scoped>

.v-list {
  height: 500px;
  overflow-y: auto
}

</style>