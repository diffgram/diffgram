<template>


  <!-- Careful with too much padding around
      here it can make it look funny with other things ie the media window-->
  <div class="d-flex flex-column" v-if="layout_type === 'large'">
    <v-alert type="info"
             icon="mdi-file-document"
             width="25%"
             class="pa-2 align-self-end" dismissible>
      Learn more about directories sync <strong> <a href="https://diffgram.readme.io/docs/job-directory-syncing"
                                                    class="white--text">clicking here</a> </strong>
    </v-alert>
    <v-layout data-cy="directories-container"
              class="d-flex flex-wrap align-content-start" style="height: 500px">

      <v-tooltip top v-for="directory in directory_list">
        <template v-slot:activator="{ on, attrs }">
          <div v-on="on"
               style="max-width: 180px;"
               :class="{'pa-2 d-flex flex-column align-center justify-center directory-container': true, 'selected': directory.selected}"
               @click="select_directory(directory.directory_id)">
            <div v-if="directory.selected" class="selected-background"></div>
            <v-icon v-if="directory.selected === 'select_once'" color="success" class="selected-check" size="32">
              mdi-checkbox-marked-circle
            </v-icon>
            <v-icon v-if="directory.selected === 'sync'" color="success" class="selected-check" size="32">
              mdi-sync-circle
            </v-icon>
            <v-icon size="96" color="primary" class="text-center">
              mdi-folder
            </v-icon>
            <p class="text-center overflow-ellipsis">{{directory.nickname}}</p>
          </div>
        </template>
        <span>{{ directory.nickname }}</span>
      </v-tooltip>

    </v-layout>
  </div>
  <div v-else class="d-flex flex-column">
    <div class="d-flex flex-column dirs-container-small">

      <div class="pb-4 d-flex flex-column flex-wrap"
           data-cy="directories-container">

        <v_directory_list class="pt-2"
                          :project_string_id="project_string_id"
                          :directory_blacklist="selected_dir_list"
                          :show_new="true"
                          :initial_dir_from_state="false"
                          :update_from_state="false"
                          :set_current_dir_on_change="false"
                          :change_on_mount="false"
                          :show_update="true"
                          @change_directory="add_to_selected_dir_list">
        </v_directory_list>


        <v-tooltip top v-for="directory in selected_dir_list">
          <template v-slot:activator="{ on, attrs }">
            <div v-on="on"
                 style="max-width: 200px;"
                 :class="{'d-flex flex-row align-center justify-center directory-container-small mb-2 pa-1': true,
                          'selected-background-small': directory.selected}">
              <v-icon size="26" color="primary" class="text-center">
                mdi-folder
              </v-icon>
              <p class="text-left overflow-ellipsis ma-0">{{directory.nickname}}</p>
              <v-icon v-if="directory.selected === 'select_once'" color="gray" class="selected-check-small"
                      @click="set_sync_dir(directory.directory_id)"
                      size="26">
                mdi-sync-circle
              </v-icon>
              <v-icon v-if="directory.selected === 'sync'" color="primary" class="selected-check-small"
                      @click="set_one_time_dir(directory.directory_id)"
                      size="26">
                mdi-sync-circle
              </v-icon>
              <v-icon color="black" class="selected-check-small ml-4" size="26"
                      @click="remove_dir(directory.directory_id)">
                mdi-close
              </v-icon>
            </div>
          </template>

          <span>{{ directory.nickname }}</span>
        </v-tooltip>
      </div>

    </div>

  </div>

</template>

<script lang="ts">

  // TODO combine directory list elements into single component
  // look at props for passing some of stuff...

  // TODO pass loading or?

  import axios from 'axios';
  import v_new_directory from './directory_new'
  import v_update_directory from './directory_update'
  import Vue from "vue";

  export default Vue.extend({
    name: 'directory_icon_selector',
    model: {
      prop: 'job',
      event: 'change'
    },
    props: {
      'project_string_id': {
        default: null
      },
      'attached_directories_list': {
        default: undefined
      },
      'job': {
        default: undefined
      },
      'layout_type': {
        default: 'large'
      },

    },
    components: {
      v_new_directory,
      v_update_directory
    },
    data() {
      return {
        directory_list: [],
        selected_dir_list: [],
        current_directory: null,

        new_directory_menu: false,
        update_directory_menu: false

      }
    },
    created() {
      // Copy dir_list to get it in local state
      if (this.$store.state.project.current && this.$store.state.project.current.directory_list) {
        this.directory_list = this.$store.state.project.current.directory_list.map(x => {
          if (this.$props.attached_directories_list) {
            for (const elm of this.$props.attached_directories_list) {
              if (elm.directory_id === x.directory_id) {
                return elm
              }
            }
          }
          return {...x, selected: undefined}
        });
      }
      // Added attached dirs if any.
      if (this.attached_directories_list) {
        for (const dir of this.attached_directories_list) {
          this.selected_dir_list.push({...dir})
        }
      }
      this.$emit('directories-updated', this.directory_list.filter(dir => dir.selected));

    },
    computed: {
      available_dirs: function () {
        const current_selected_dir_ids = this.selected_dir_list.map(dir => dir.directory_id);
        return this.$store.state.project.current.directory_list.map(dir => ({
          ...dir,
          icon: 'mdi-folder',
          color: 'primary'
        })).filter(dir => {
          return !current_selected_dir_ids.includes(dir.directory_id);
        })
      }
    },
    methods: {
      add_to_selected_dir_list: function (dir) {
        if (this.selected_dir_list.filter(elm => elm.directory_id === dir.directory_id).length > 0) {
          this.$emit('directories-updated', this.selected_dir_list);
          return
        }
        this.selected_dir_list.push({...dir, selected: 'sync'})
        this.job.attached_directories_dict.attached_directories_list = [...this.selected_dir_list];
        this.$emit('directories-updated', this.selected_dir_list);
      },
      remove_dir: function (dir_id) {
        this.selected_dir_list = this.selected_dir_list.filter(
          elm => elm.directory_id !== dir_id
        )
        this.job.attached_directories_dict.attached_directories_list = [...this.selected_dir_list];
        this.$emit('directories-updated', this.selected_dir_list);
      },
      set_sync_dir: function (dir_id) {
        this.selected_dir_list = this.selected_dir_list.map(e => {
          if (dir_id === e.directory_id) {
            return {
              ...e,
              selected: 'sync'
            }
          }

          return {
            ...e
          }
        })
        this.job.attached_directories_dict.attached_directories_list = [...this.selected_dir_list];
        this.$emit('directories-updated', this.selected_dir_list);
      },
      set_one_time_dir: function (dir_id) {
        this.selected_dir_list = this.selected_dir_list.map(e => {
          if (dir_id === e.directory_id) {
            return {
              ...e,
              selected: 'select_once'
            }
          }
          return {
            ...e
          }
        })
        this.job.attached_directories_dict.attached_directories_list = [...this.selected_dir_list];
        this.$emit('directories-updated', this.selected_dir_list);
      },
      select_directory: function (id) {
        this.directory_list = this.directory_list.map(dir => {
          if (dir.directory_id === id) {
            let new_selected = undefined;
            if (!dir.selected) {
              new_selected = 'sync'
            } else if (dir.selected === 'sync') {
              new_selected = 'select_once';
            } else if (dir.selected === 'select_once') {
              new_selected = undefined;
            }
            return {
              ...dir,
              selected: new_selected
            }
          }
          return dir
        })
        this.job.attached_directories_dict.attached_directories_list = [...this.selected_dir_list];
        this.$emit('directories-updated', this.directory_list.filter(dir => dir.selected));
      }
    },
  })
</script>
<style scoped>
  .overflow-ellipsis {
    width: 150px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .dirs-container {
    background: #f7f7f7;

  }

  .dirs-container-small {
    max-height: 500px;
    overflow-y: auto;

  }

  .selected-check {
    position: absolute;
    left: 0px;
    top: 0px;

  }

  .selected-check-small:hover {
    cursor: pointer;
  }

  .selected-background {
    background: #0D47A1;
    height: 150px;
    width: 150px;
    position: absolute;
    opacity: 0.3;
  }

  .selected-background-small {
    border: 2px solid #1a76d2;
    border-radius: 5px;
  }

  .directory-container-small {
    background: #f7f7f7;
    border: 2px solid #e6e6e6;

  }

  .directory-container:hover{
    cursor: pointer;
  }

</style>
