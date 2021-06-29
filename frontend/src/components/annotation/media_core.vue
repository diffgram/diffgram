<template>

<!-- Until we have a better way, don't show if task id.
     Since by definition a task only has 1 file attached to it
     showing this at all doesn't make sense, and since we have added functions
     it takes up a lot of space / things that don't make sense with it

    We use job id not task id here because when we run out of tasks, we want it to
    show None here
    -->

  <!-- TODO do show if job id and in attach to job mode-->

<div v-cloak v-if="!task" id="media_core" style="border-top: 1px solid #dcdbdb">
  <v-card >

    <!-- TODO make this a bit smarter,
      ie if server side total == total shown etc...-->

    <v-alert class="text-left"
            :value="select_from_metadata"
            type="warning">
    Heads Up! You have selected all results ({{all_selected_count}} files).
    This includes server side results which <b> may not be displayed.</b>
    </v-alert>

    <v-alert v-if="!loading && !media_loading && file_list.length == 0"
             type="info">
      <v-layout>

        <p class="pr-4">
          No files match criteria. Change criteria and refresh. Or import new data.
        </p>

        <v-btn :disabled="!$store.state.project.current.project_string_id"
                color="primary"
                @click="$router.push('/studio/upload/' +
                          $store.state.project.current.project_string_id)">

            <v-icon left>cloud_upload</v-icon>
            Import
        </v-btn>
      </v-layout>

    </v-alert>

    <v_info_multiple  class="text-left"
                     :info="info">
    </v_info_multiple>


    <v-layout >

          <div >


            <v-toolbar
                dense
                elevation="1"
                fixed
                height="50"
                >
            <v-toolbar-items>

              <v_directory_list
                  class="pt-4"
                  :project_string_id="project_string_id"
                  :show_new="false"
                  :show_update="false"
                  :change_on_mount="false"
                  :set_from_id="current_dataset.directory_id"
                  v-if="file_dirs_view_mode === 0"
                  @change_directory="change_directory($event)">
              </v_directory_list>


              <v-divider
                vertical
              ></v-divider>

              <div v-if="!media_loading && !loading && metadata_previous.start_index == metadata_previous.file_count">
                 <v-chip color="white"
                      text-color="primary"
                      >No more pages.</v-chip>
              </div>
              <div v-else
                   class="pl-2 pt-4">

                <v-chip color="white"
                        text-color="primary"
                    >{{start_index_oneth_index}} to
              {{metadata_previous.end_index }} </v-chip>
                of
                <v-chip class="pl-2 pr-2"
                        color="white"
                        text-color="primary"
                    >{{metadata_previous.file_count}}</v-chip>

              </div>

              <!-- Note show conditions are different for next / previous
                and show conditions are inverted as opposed to disable-->
              <!-- Only show next/previous page if it exists, saves real estate vs disabling-->
              <div>
                <tooltip_button
                  v-show="!loading &&
                      metadata_previous.start_index != 0"
                  tooltip_message="Previous Page"
                  @click="previous_page"
                  :loading="loading"
                  :icon_style="true"
                  icon="mdi-chevron-left-box"
                  color="primary"
                >
                </tooltip_button>

                <tooltip_button
                  v-show="!loading &&
                      (metadata_previous.end_index != metadata_previous.file_count
                      || metadata_previous.next_page != undefined)"
                  tooltip_message="Next Page"
                  @click="next_page"
                  :loading="loading"
                  :icon_style="true"
                  icon="mdi-chevron-right-box"
                  color="primary"
                >
                </tooltip_button>
              </div>


              <v-divider
                vertical
              ></v-divider>


              <v-text-field label="Search"
                            v-model="search_term"
                            @change="request_media()"
                            clearable
                            class="pa-4"
                            @focus="$store.commit('set_user_is_typing_or_menu_open', true)"
                            @blur="$store.commit('set_user_is_typing_or_menu_open', false)"
              >

              </v-text-field>

              <tooltip_button
                tooltip_message="Refresh Media"
                @click="request_media"
                :loading="loading"
                :icon_style="true"
                :bottom="true"
                icon="mdi-refresh"
                color="primary"
              >
              </tooltip_button>

            <!-- Filters -->
            <button_with_menu
              v-if="file_dirs_view_mode === 0"
              tooltip_message="Filters"
              icon="mdi-filter"
              :close_by_button="true"
              offset="x"
              color="primary"
              :commit_menu_status="true"
            >

              <template slot="content">

                <v-select
                  :items="metadata_limit_options"
                  v-model="metadata_limit"
                  label="Results Per Page:"
                  item-value="text"
                  :disabled="loading"
                  @change="item_changed"></v-select>

                <v-layout>

                  <v-select

                    v-model="issues_filter"
                    :items="issue_filter_options"
                    :clearable="true"
                    label="Filer by Issues"
                    item-text="name"
                    item-value="value"
                  ></v-select>
                  <v-select v-if="file_view_mode != 'task' && job_list.length != 0"
                            :items="job_list"
                            v-model="job"
                            label="Job"
                            return-object
                            item-text="name"
                            :disabled="loading || job_list_loading"
                            @focus="job_list_api()"
                            @change="item_changed"></v-select>


                  <v-select :items="annotation_status_options"
                            v-model="annotation_status"
                            label="Status"
                            item-value="text"
                            :disabled="loading"
                            @change="item_changed"></v-select>

                  <!-- Actions API only -->
                  <div v-if="$store.state.user.current.api
                   && $store.state.user.current.api.api_actions">
                    <v-select :items="annotations_are_machine_made_items"
                              v-model="annotations_are_machine_made_setting"
                              label="Instance Type"
                              item-value="text"
                              :disabled="loading"
                              @change="item_changed"></v-select>
                  </div>

                  <v-select :items="filter_media_type_option_list"
                            v-model="filter_media_type_setting"
                            label="File Type"
                            item-value="text"
                            :disabled="loading"
                            @change="item_changed"></v-select>


                </v-layout>

                <date_picker class="pt-2 pr-4" @date="date = $event"
                              :with_spacer="false"
                              :initialize_empty="true">

                </date_picker>



              </template>

            </button_with_menu>


              <v-divider
                vertical
              ></v-divider>


              <!-- File Actions (Move, Delete, Copy, etc) section -->

              <button_with_menu
                tooltip_message="Transfer Selected Files"
                v-if="!view_only_mode && !anonymous_user_in_public_project"
                icon="mdi-file-move"
                color="primary"
                :loading="api_file_update_loading"
                :disabled="selected.length == 0"
                offset="x"
                :bottom="true"
              >
                <template slot="content">

                  <v_file_transfer
                    :project_string_id="project_string_id"
                    :source_directory="current_dataset"
                    :file_list="selected"
                    :select_from_metadata="select_from_metadata"
                    :metadata_previous="metadata_previous"
                  >
                  </v_file_transfer>

                </template>
              </button_with_menu>


              <button_with_menu
                :value="menu_for_remove_files_bool"
                icon="delete"
                tooltip_message="Remove Selected Files"
                color="primary"
                :loading="api_file_update_loading"
                :disabled="api_file_update_loading || selected.length == 0"
                v-if="!view_only_mode && !anonymous_user_in_public_project && ['annotation'].includes(file_view_mode)"
                :icon_style="true"
                :bottom="true"
              >
                <template slot="content">

                  <v-layout column>
                    <v-row>
                      <v-col cols="12">
                        <v-card-title>Are you sure you want to delete the files?</v-card-title>
                        <v-card-text>
                          You will not be able to view, copy, or edit any instances of the
                          files after deleting them.
                        </v-card-text>

                        <v-checkbox v-model="cascade_archive_tasks"
                                    label="Delete all related tasks from the selected files too.">
                        </v-checkbox>

                        <v-btn small color="error"
                               @click="api_file_update('REMOVE'),
                                     menu_for_remove_files_bool = false">
                          <v-icon>mdi-delete</v-icon>Confirm Delete
                        </v-btn>
                      </v-col>
                    </v-row>
                  </v-layout>

                </template>
              </button_with_menu>

              <!-- Pending removal -->
              <!--
              <div v-if="$store.state.user.current.api
               && $store.state.user.current.api.api_actions">

                <tooltip_button
                  @click="inference_selected()"
                  icon="mdi-rocket"
                  tooltip_message="Inference"
                  color="red"
                  v-if="['annotation'].includes(file_view_mode)"
                  :disabled="inference_selected_loading
                   || selected.length == 0
                   || select_from_metadata"
                  :icon_style="true"
                  :bottom="true"
                >
                </tooltip_button>

                <v_error_multiple :error="error_inference">
                </v_error_multiple>

              </div>
              -->

            <v-divider
              vertical
            ></v-divider>


            <!-- LAYOUT SELECT -->
            <button_with_menu
              tooltip_message="Layout"
              icon="mdi-view-grid"
              color="primary"
              v-if="file_dirs_view_mode === 0"
              :close_by_button="true"
            >

              <template slot="content">
                <v-layout column>

                  <v-select
                    :items="layout_list"
                    v-model="layout_view"
                    label="Layout"
                    @change="prevent_refresh_on_layout_change = true"
                    :disabled="loading">

                    <template v-slot:item="{ item, title }">

                      <v-icon left>
                        {{item.icon}}
                      </v-icon>

                      {{ item.text}}

                    </template>

                    <template v-slot:selection="{ item, title }">

                      <v-icon left>
                        {{item.icon}}
                      </v-icon>

                      {{ item.text}}

                    </template>

                  </v-select>
                </v-layout>

              </template>
            </button_with_menu>

            <button_with_menu
              tooltip_message="Column Visibility"
              icon="mdi-format-columns"
              :close_by_button="true"
              v-if="!view_only_mode && layout_view == 'list'"
              offset="x"
              color="primary">

              <template slot="content">

                <v-select :items="headers"
                          v-model="headers_selected"
                          multiple
                          label="Column Visibility"
                          :disabled="loading">
                </v-select>

                <tooltip_button
                  tooltip_message="Reset"
                  @click="headers_selected = headers_selected_backup"
                  v-if="headers_selected != headers_selected_backup"
                  icon="autorenew"
                  color="primary">
                </tooltip_button>

              </template>

            </button_with_menu>


              <v-divider
                vertical
              ></v-divider>



              <button_with_menu
                tooltip_message="Quick Help"
                icon="mdi-lifebuoy"
                color="primary"
                :close_by_button="true"
              >
                <template slot="content">
                  <v-layout column>

                    <v-alert type="info" dismissible>
                      <kbd>control</kbd> + click to select files in icon mode.
                    </v-alert>

                    <v-alert type="info" dismissible>
                      Click minimize / open File Explorer as needed.
                    </v-alert>

                  </v-layout>
                </template>

              </button_with_menu>


             </v-toolbar-items>

            </v-toolbar>




            <!-- Deprecated ? -->
            <!--
            <div class="pa-0 d-flex flex-column" v-if="file_view_mode === 'task'">
              <v-btn-toggle
                color="primary"
                v-model="file_dirs_view_mode"
                mandatory
              >
                <v-btn class="text-body-2" small>
                  Select Files
                </v-btn>
                <v-btn small>
                  Select Datasets
                </v-btn>
              </v-btn-toggle>
            </div>
            -->



            <v-alert :value="run_FAN_success" type="info" dismissible>
              Running. Please wait.
              Warm up takes about 1 minute. Then about 1 second per image or frame.
              If you have selected at least 6 images you will receive an email when inference is complete.
              Click the image to refresh the file and see results.

            </v-alert>

            <div v-if="file_dirs_view_mode === 1">

              <dir_attach :project_string_id="project_string_id"
                          :file_list="file_list"
                          :selected="selected_dirs"
                          :job_id="job_id"
              >
              </dir_attach>

            </div>
            <div v-if="file_view_mode == 'task' && file_dirs_view_mode === 0">

              <v_task_file_attach :project_string_id="project_string_id"
                                  :file_list="file_list"
                                  :selected="selected"
                                  :job_id="job_id"
                                  :select_from_metadata="select_from_metadata"
                                  :metadata_previous="metadata_previous"
              >
              </v_task_file_attach>

            </div>




          </div>

    </v-layout>

    <!-- Want to be careful if statements show up here otherwise a bunch of empty space -->

    <v-card-subtitle v-if="selected.length != 0 && file_view_mode != 'task'">

      <v-layout>
        <div class="pr-2 pl-2">
          <v-chip   color="blue"
                    text-color="white"
                    >{{all_selected_count}}</v-chip>
            Selected
        </div>

        <v-checkbox :label="'Select all ' + metadata_previous.file_count + ' results'"
                    v-model="select_from_metadata"
                    @change="select_all"
                    >
        </v-checkbox>
      </v-layout>

    </v-card-subtitle>


    <template v-if="file_dirs_view_mode === 0">
      <!-- ICONS / grid LAYOUT -->
      <!-- I would like to use a
         style="max-height: 50px"
        or something but it doesn't quite work
        (overflows y funny)
        -->
      <v-card class="pa-4" elevation-1
              v-if="layout_view == 'icons' ">

        <v-skeleton-loader
          :loading="media_loading"
          type="date-picker-days"
          :tile="true"
        >
          <v-container container--fluid
                       grid-list-md
                       style="overflow-x:auto"
          >
            <v-layout :style="full_screen ? {display: 'flex', flexWrap: 'wrap'}: undefined">

              <v-row align="end"
                     v-if="file_list.length === 0"
                     class="pa-4"
                     justify="center">

                <!-- Value of being inside Media Browser to help understand that connection.
                     Like that thing Conor was saying about actions being close to the context

                     For alignment consider how it looks with media,
                     and case of no media. ie with no media looks nicer to center perhaps.
                -->
                <tooltip_button
                  tooltip_message="Add Media"
                  @click="$router.push('/studio/upload/' +
                              $store.state.project.current.project_string_id)"
                  icon="mdi-plus-box-multiple"
                  :large="true"
                  :icon_style="true"
                  color="primary">
                </tooltip_button>
              </v-row>

              <v-card xs4
                      md1
                      elevation="1"
                      class="pa-2 ma-2"
                      v-for="(item, index) in file_list"
                      :key="index"
                      style="display: flex; flex-wrap: wrap"
              >
                <a @click="change_file_request(item)">
                  <div v-if="current_file && item.id == current_file.id">

                    <!-- Badge thing actually seems to make it worse here -->
                    <!--
                    <v-badge color="primary">
                      <v-icon dark slot="badge">check</v-icon>
                    </v-badge>
                    -->
                    <tooltip_icon
                      tooltip_message="Current File"
                      icon="check"
                      color="primary">
                    </tooltip_icon>

                  </div>

                  <div v-if="item.attached_to_job==true">
                    <tooltip_icon
                      tooltip_message="Attached"
                      icon="mdi-check-all"
                      color="green">
                    </tooltip_icon>
                  </div>

                  <div>

                    <thumbnail
                      v-if="item.type === 'video' || item.type === 'image'"
                      :item="item"
                      :selected="selected"
                      @on_image_error="on_image_error(index)"
                    >
                    </thumbnail>
                    <v-container class="d-flex flex-column justify-center align-center"
                                 style="width: 100px; height: 100px; border: 1px solid #bdbdbd;" v-else>
                      <v-icon>
                        mdi-script-text
                      </v-icon>
                      <p class="mt-4">{{item.original_filename}}</p>
                    </v-container>

                  </div>
                </a>

                <!--
              <v-btn icon @click="delete_function(item, index)">
                <v-icon color="primary" small> delete </v-icon>
              </v-btn>
                  -->
              </v-card>
            </v-layout>
          </v-container>

        </v-skeleton-loader>

      </v-card>
      <!-- END ICONS LAYOUT -->

      <!-- LIST LAYOUT -->
      <!--
         Jan 21, 2020 Re: server-items-length, length_current_page
            Careful that the value here works in context of JOB stuff too.
            Context that (at time of writing) length_current_page includes
            files in the job, where as the file_count doesn't AND
            that data table takes this value 'strictly' in a bad way,
            ie it won't show any files if the value is 0 even if it has items in
            file_list.
      -->
      <v-card style="overflow-y:auto; max-height: 600px">
        <v-data-table v-if="layout_view == 'list'"
                      :headers="headers_view"
                      :items="file_list"
                      class="elevation-1"
                      :options.sync="options"
                      :server-items-length="metadata_previous.length_current_page"
                      item-key="id"
                      hide-default-footer
                      v-model="selected"
                      :show-select="select_all_data_table">

          <!-- appears to have to be item for vuetify syntax-->
          <template slot="item" slot-scope="props">

            <tr>
              <td v-if="file_view_mode != 'home'">
                <v-checkbox v-model="props.isSelected"
                            @change="props.select($event)"
                            primary>
                </v-checkbox>
              </td>

              <td v-if="file_view_mode == 'task' ">
                <div v-if="props.item.attached_to_job==true">
                  <v-icon color="green">mdi-check-all</v-icon>
                </div>
              </td>

              <td v-if="file_view_mode == 'changes' ">
                <div v-if="props.item.state=='added'">
                  <v-icon color="green">add_circle</v-icon>
                </div>
                <div v-if="props.item.state=='removed'">
                  <v-icon color="red">remove_circle</v-icon>
                </div>
                <div v-if="props.item.state=='changed'">
                  <v-icon color="orange">fiber_manual_record</v-icon>
                </div>
              </td>

              <td v-if="show_column('preview_image')"
                  @click="change_file_request(props.item)">
                <div v-if="current_file && props.item.id == current_file.id">

                  <v-badge overlap color="primary">
                    <v-icon dark slot="badge">check</v-icon>
                  </v-badge>

                </div>


                <thumbnail
                  :item="props.item"
                  :selected="selected"
                  @on_image_error="on_image_error(index)"
                >
                </thumbnail>


              </td>

              <td v-if="show_column('type')">

                <div v-if="props.item.type == 'image'">
                  <v-icon alt="props.item.type">image</v-icon>
                </div>
                <div v-if="props.item.type == 'video'">
                  <v-icon alt="props.item.type">mdi-file-video</v-icon>
                </div>
                <div v-if="props.item.type == 'label'">
                  <v-icon alt="props.item.type">label</v-icon>
                </div>

              </td>

              <td v-if="show_column('filename')">

                {{props.item.original_filename}}

              </td>

              <td v-if="show_column('created_time')">
                {{props.item.created_time | moment("dddd, MMMM Do H:mm:ss a") }}
              </td>

              <td v-if="show_column('time_last_updated')">
                {{props.item.time_last_updated | moment("dddd, MMMM Do H:mm:ss a") }}
              </td>

              <td v-if="show_column('complete')">

                <!--
                     Not clear value of having this here.
                     How / why would someone want to complete / not complete a file in this preview mode?
                     And if they really did, would probably make more sense as a bulk operation?
                     Either way it's taking up a lot of screen space.

                     And as we move to iterative "building" up of files,
                     the "complete" only makes sense more in task mode?
                    -->

                <!-- Don't need tool tip if we have header -->
                <v-icon color="green"
                        v-if="props.item.ann_is_complete">
                  mdi-check-circle
                </v-icon>


              </td>

              <!--
    <v-btn icon @click="annotation_example_toggle_function(props.item, index)">

      <div v-if="props.item.is_annotation_example == true">
        <v-icon color="primary" small> flag </v-icon>
      </div>
      <div v-else>
        <v-icon color="primary" small> flag </v-icon>
      </div>
    </v-btn>
        -->

              <td v-if="show_column('actions')">

                <v-btn v-if="['annotation'].includes(file_view_mode)"
                       icon @click="remove_function(props.item)">
                  <v-icon color="primary" small> delete </v-icon>
                </v-btn>

              </td>
            </tr>
          </template>

          <div v-if="!loading">
            <v-alert slot="no-data"  color="error" icon="warning">
              No results found.
            </v-alert>
          </div>

        </v-data-table>
      </v-card>
      <!-- END ICONS LAYOUT -->

      <div v-if="file_view_mode == 'changes'">

        <v_source_control_commit
          :project_string_id="project_string_id"
          :file_list="file_list"
          :selected="selected"
          :select_from_metadata="select_from_metadata"
          :metadata_previous="metadata_previous"
          @request_media="request_media">

        </v_source_control_commit>

      </div>
    </template>
    <template v-if="file_dirs_view_mode === 1">
      <v-card class="pa-4" elevation-1>

        <v-skeleton-loader
          :loading="media_loading"
          type="date-picker-days"
          height="500px"
          :tile="true"
        >
          <directory_icon_selector
            class="pt-2"
            :project_string_id="project_string_id"
            :attached_directories_list="job_attached_dirs"
            @directories-updated="on_directories_updated"
          >

          </directory_icon_selector>

        </v-skeleton-loader>

      </v-card>
    </template>

  </v-card>

</div>
</template>

<script lang="ts">
// @ts-nocheck

import axios from 'axios';
import v_file_transfer from '../source_control/file_transfer'
import directory_icon_selector from '../source_control/directory_icon_selector'
import dir_attach from '../task/file/dir_attach'

import Vue from "vue";

 export default Vue.extend( {
  name: 'media_core',
  components: {
    v_file_transfer,
    directory_icon_selector,
    dir_attach,
   },
    props: {
      'project_string_id': {
        default: null
      },
      'full_screen': {
        default: false
      },
      'file_id_prop': {
        default: null
      },
      'job_id': {
        default: null
      },
      'job': {
        default: null
      },
      'file_view_mode': {
        default: null  // home, task, changes, annotation
      },
      'view_only_mode': {
        default: false
      },
      'task': {
       },
      'visible': {
        type: Boolean,
        default: false
       },


    },
  watch: {
    'request_next_page': 'next_page',
    '$route': 'request_media',

    'visible' : 'refresh_component_sizes',

    options: {
      handler () {

        // hacky wraper to get around vuetify data table doing this
        // on reload
        if (this.prevent_refresh_on_layout_change == false) {
          this.request_media()
        }
        else {
          this.prevent_refresh_on_layout_change = false
        }
      },
      deep: true
    }
  },

  data() {
    return {
      issues_filter: undefined,
      issue_filter_options: [
        {name: 'Filter By Files With Open Issue', value: 'open_issues'},
        {name: 'Filter By Files With Closed Issues', value: 'closed_issues'},
        {name: 'Filter By Files Any Issues', value: 'issues'},
      ],

      menu_for_remove_files_bool: undefined,
      metadata_previous: {
        file_count: null
      },

      current_dataset: {},
      current_file: null,
      request_next_page: null,
      file_list: [],

      height: 0,
      page_number: 1,
      selected_dirs: [],
      job_attached_dirs: [],
      select_from_metadata: false,
      media_loading: false,
      cascade_archive_tasks: false,

      prevent_refresh_on_layout_change: false,

      layout_view: "icons",
      layout_list : [
        {text: "List",
         value: "list",
         icon: "mdi-format-list-bulleted"
        },
        {text: "Medium Icons",
         value: "icons",
         icon: "mdi-grid"
          }
        ],

      error_inference: {},

      selected: [],

      options : {
        'sortDesc': [true],
        'itemsPerPage': -1
      },
      // -1 for all since we have a limit on how many we show, so makes sense to show all here right?

      info: {},

      run_FAN_success: false,
      job_list_loading : false,
      file_dirs_view_mode: 0,

      api_file_update_loading: false,

      loading: true,
      inference_selected_loading: false,

      filter_media_type_option_list: ["All", "Image", "Video"],
      filter_media_type_setting: "All", // Video

      annotations_are_machine_made_items: ["All", "Predictions only", "Human only"],
      annotations_are_machine_made_setting: "All",

      annotation_status_options: ["All", "Completed", "Not completed"],
      annotation_status: "All",

      metadata_limit_options: [10, 25, 100, 250, 950],
      metadata_limit: 25, // TODO attach to vue store.

      job_list: [],
      date: undefined,

      instance_changes: [],

      current_video: {
        id: null
      },

      headers_selected: [
        "preview_image",
        "type",
        "created_time",
        "filename",
        "complete",
        "actions"
        ],

      headers_selected_backup : [],  // copied from headers_selected during mounted

      headers: [
        {
          text: "File",
          align: 'left',
          sortable: false,
          value: 'preview_image'
        },
        {
          text: "Type",
          align: 'right',
          sortable: false,
          value: 'type'
        },
        {
          text: "Filename",
          value: "filename",
          align: 'right',
          sortable: true,
        },
        {
          text: "Created",
          align: 'right',
          sortable: true,
          value: 'created_time'
        },
        {
          text: "Last Updated",
          align: 'right',
          sortable: true,
          value: 'time_last_updated'
        },
        {
          text: "Complete",
          align: 'right',
          sortable: false,
          value: 'complete'
        },
        {
          text: "Actions",
          align: 'right',
          sortable: false,
          value: 'actions'
        }
      ],
      headers_with_state: [
        {
          text: "State",
          align: 'left',
          sortable: false,
        },
        {
          text: "File",
          align: 'left',
          sortable: false,
          value: 'url_signed_thumb'
        },
        {
          text: "Type",
          align: 'left',
          sortable: true,
          value: 'type'
        },
        {
          text: "Actions",
          align: 'left',
          sortable: false,
        }
      ],
      headers_task: [

        {
          text: "Status",
          align: 'left',
          sortable: true,
          value: 'attached_to_job'
        },
        {
          text: "File",
          align: 'left',
          sortable: false,
          value: 'url_signed_thumb'
        },
        {
          text: "Type",
          align: 'left',
          sortable: true,
          value: 'type'
        }
      ],

      control_key_down : false,

      search_term: null


    }
  },
  computed: {
    anonymous_user_in_public_project: function(){
      if(this.$store.getters.is_on_public_project && !this.$store.state.user.logged_in){
        return true
      }
      else{
        return false;
      }
    },
    select_all_data_table: function () {
      if (this.file_view_mode == "home") {
        return false
      } else {
        return true
      }
    },

    all_selected_count: function () {

      if (this.select_from_metadata == false) {
        return this.selected.length
      }
      else {
        return this.metadata_previous.file_count
      }

    },

    start_index_oneth_index: function() {
      return this.metadata_previous.start_index + 1
    },

    headers_view: function () {

      // why 2 == null methods here?
      // TODO review this
      if (this.file_view_mode == null) {
        return this.headers_with_state
      }

      if (this.file_view_mode == "task") {
        return this.headers_task
      }

      let output_headers = []
      for (let header of this.headers) {
        if (this.show_column(header.value)){
          output_headers.push(header)
        }
      }

      return output_headers

    },

    metadata: function () {

      // TODO better way to handle this
      // We have dict job for job_list selection (Browsing multiple jobs)
      // BUT sometimes only have the raw job_id sigh

      let job_id = this.job_id
      if (!job_id && this.job) {
        job_id = this.job.id
      }

      return {
        'directory_id': this.current_dataset.id || this.current_dataset.directory_id,
        'date_from': this.date ? this.date.from : undefined,
        'date_to': this.date ? this.date.to : undefined,
        'annotations_are_machine_made_setting': this.annotations_are_machine_made_setting,
        'annotation_status': this.annotation_status,
        'issues_filter': this.issues_filter,
        'limit': this.metadata_limit,
        'media_type': this.filter_media_type_setting,
        'page': this.page_number,
        'file_view_mode': this.file_view_mode,
        'previous': this.metadata_previous,
        'options': this.options,
        'job_id': job_id,
        'search_term': this.search_term
      }

    }

  },
  mounted() {

    setTimeout(() => {
      this.refresh_component_sizes()
    }, 750)

    this.determine_intial_dataset_strategy(),

    window.addEventListener('keydown', this.keyboard_events_global_down)
    window.addEventListener('keyup', this.keyboard_events_global_up)

    if (window.innerWidth < 1200) {
      // old
    }

    if (this.file_view_mode == 'task') {
      this.layout_view = "list"
    }

    this.headers_selected_backup = this.headers_selected

    this.request_media()

    // ie triggered by  this.$store.commit('init_media_refresh')
    var self = this
    this.media_refresh_watcher = this.$store.watch((state) => { return this.$store.state.media.refresh },
      (new_val, old_val) => {
        self.request_media()
      },
    )

    this.loading = false
    if(this.$props.job && this.$props.job.attached_directories_dict){
      this.job_attached_dirs = this.$props.job.attached_directories_dict.attached_directories_list;
    }

  },

  beforeDestroy() {
    window.removeEventListener('keydown', this.keyboard_events_global_down)
    window.removeEventListener('keyup', this.keyboard_events_global_up)

    this.media_refresh_watcher() // destroy watcher
  },

  methods: {
    update_file_list_and_set_current_file: async function (file_list_data) {
      this.metadata_previous = file_list_data.metadata;
      this.file_list = file_list_data.file_list;
      this.$emit('file_list_length', this.file_list.length);
      this.current_file = this.file_list[0]
    },

    get_media: async function (fetch_single_file = true, file_id) {

      this.loading = true
      this.error = {}   // reset
      this.media_loading = true;

      if ((this.$props.file_id_prop && fetch_single_file) || file_id) {
        if(file_id != undefined){
          await this.fetch_single_file(file_id);
        }
        else{
          await this.fetch_single_file(this.$props.file_id_prop);
        }
        const current_file = {...this.file_list[0]};
        const file_list_data = await this.fetch_project_file_list();
        const is_current_file_in_list = file_list_data.file_list.filter(f => f.id === current_file.id).length > 0;
        if(!is_current_file_in_list){
          file_list_data.file_list.unshift(current_file);
        }
        else{
          let index = -1;
          for(let i = 0; i < file_list_data.file_list.length; i++){
            let file = file_list_data.file_list[i]
            if(file.id === current_file.id){
              index = i;
              break;
            }
          }
          if(index != -1){
            file_list_data.file_list.splice(index,1);
            file_list_data.file_list.unshift(this.file_list[0]);
          }

        }

        this.append_project_file_list(file_list_data);
        this.update_file_list_and_set_current_file(file_list_data);

        this.media_loading = false;
        this.loading = false;
        this.current_file = current_file;
        return current_file;
      }
      else if (this.$props.project_string_id)  {
        const file_list_data = await this.fetch_project_file_list();
        await this.update_file_list_and_set_current_file(file_list_data);
        this.media_loading = false;
        this.loading = false;
        return this.current_file;
      }


    },
    set_file_list: function(new_file_list){
      this.file_list = new_file_list;
    },
    append_project_file_list: async function (file_list_data) {
      const file_ids = this.file_list.map(file => file.id);
      for (let i = 0; i < file_list_data.file_list.length; i++) {
        const current = file_list_data.file_list[i];
        if(!file_ids.includes(current.id)){
          this.file_list.push(current)
        }

      }
      this.$emit('file_list_length', this.file_list.length);
    },
    fetch_project_file_list: async function(){
      this.error_no_permissions = {};
      try{
        const response = await axios.post('/api/project/' + String(this.$props.project_string_id) +
          '/user/' + this.$store.state.user.current.username + '/file/list', {

          'metadata': this.metadata,
          'project_string_id': this.$props.project_string_id

        })
        if (response.data['file_list'] != null) {
          return response.data;
        }
      }
      catch(error){
        const { response } = error;
        if(response.status === 403){
          this.error_no_permissions = {
            data: response.data,
            status: response.status,
            message: 'You are not allowed to view this resource, please contact the project admin to get permissions.'
          };
          this.$emit('permissions_error', this.error_no_permissions)
        }
        console.error(error);
        this.loading = false
        // this.logout()
      }
    },
    fetch_single_file: async function(file_id){
      // why would we need metadata from request media here?
      if(!file_id){
        throw Error('Provide file_id to fetch file [on fetch_single_file()]')
      }
      try{
        const response = await axios.post('/api/v1/file/view', {
          'file_id': parseInt(file_id),
          'project_string_id': this.$props.project_string_id
        })
        this.file_list = [response.data['file']]

        this.$emit('file_list_length', this.file_list.length)
        this.metadata_previous = this.metadata;
        // should we reset or clear metadata previous?

        // WIP for future feature, ie if we don't have project permissions.
        if (response.data.label_dict && response.data.label_dict.label_file_colour_map) {
          this.label_file_colour_map = response.data.label_dict.label_file_colour_map
          this.label_list = response.data.label_dict.label_list
        }
        return response.data['file']
      }catch(error){
        this.error = this.$route_api_errors(error)
        this.loading = false
      }
    },
    determine_intial_dataset_strategy: function () {
      if (this.$route.query["dataset"]) {
        this.current_dataset.directory_id = parseInt(this.$route.query["dataset"])
      }
      else {
        // Default
        // I feel like the interaction with directory_list here is a little bit confused.
        // This needs some work! eg right now directory list could potentially
        // display a different dir then what's set here.
        // Maybe directory_list could watch the route query params instead?
        // That selector is already kinda 'overloaded' though
        this.current_dataset = this.$store.state.project.current_directory
      }
      // Not sure if we want something else from vuex here?
      // like load last used dataset or something...

    },
    on_directories_updated: function(dirs){
      this.selected_dirs = dirs;
    },
    refresh_component_sizes: function () {
      /*
       * Why timeout?
       *  1) Animation?
       *  2) and other stuff... delay
       *  https://github.com/vuejs/Discussion/issues/394
       *
       */
      setTimeout(() => {
        this.height = this.$el.clientHeight
        // careful, height of 0 is ok
        if (this.height != undefined) {
         this.$emit('height',  this.height)
        }
      }, 350)
    },

    on_image_error: function (index) {
      // Note if we want both the event and something else like index
      // ie seems like we need to do on_image_error($event, index) when calling it

      // Jan 8th, 2020, there is still something funny with the
      // way this gets "propogated"
      // when using the vuetify iamge thing...

      this.file_list[index].frontend_src_load_failed = true

    },

    select_all(){
      if (this.select_from_metadata == true) {
        this.selected = this.file_list
      }
      if (this.select_from_metadata == false) {
        this.selected = []
      }
    },

    keyboard_events_global_down(event) {

      if (event.key == "Control") {
        this.control_key_down = true
      }

    },

    keyboard_events_global_up(event) {

      if (event.key == "Control") {
        this.control_key_down = false
      }

    },

    select_from_something(file) {

      // only enable for icon view for now
      if (this.layout_view != "icons") {
        return
      }

      let existing_index = this.selected.indexOf(file)

      if (existing_index != -1) {
        this.selected.splice(existing_index, 1)
      }
      else {
        this.selected.push(file)
      }


    },

    change_directory(event) {

      this.current_dataset = event

      this.$addQueriesToLocation({'dataset' : event.directory_id})
      this.page_number = 1;

      this.get_media(false);


    },

    show_column(column_name){
      return this.headers_selected.includes(column_name)
    },

    job_list_api() {

      // Return if we already have job list
      // since at the moment we call this on every @focus event
      if (this.job_list.length != 0) {
        return
      }

      this.job_list_loading = true

      axios.post('/api/v1/job/list', {

        metadata: {
          'my_jobs_only': true,
          'builder_or_trainer': this.$store.state.builder_or_trainer,
          'data_mode': 'name_and_id_only',
          'project_string_id': this.$props.project_string_id
        }

      }).then(response => {

        if (response.data['Job_list'] != null) {

          this.job_list = response.data['Job_list']
          this.job_list_loading = false

        }

      })
        .catch(error => {
          console.error(error);
          this.loading = false
          this.logout()
        });
    },
    async change_file(direction, file){
      if(direction != 'next' && direction != 'previous' && !file){
        throw new Error('direction must be either "next" or "previous", else provide a specific file to set as second param.')
      }
      if(!file){
        let i = null;
        let file_id = null
        file_id = this.current_file.id
        i = this.file_list.findIndex(x => x.id == file_id)
        var original_i = i
        if (direction === "next") {
          i += 1
        } else { i -= 1 }

        // limits
        if (i < 0 && this.page_number > 1) {
          await this.previous_page();
          i = this.file_list.length - 1
        }
        else if(i < 0 && this.page_number == 1){
          i = 0
        }
        // End of list, go to next page
        else if (i >= this.file_list.length) {
          // Auto Advance to next page
          // Check is to help it not jump if at "end of list"?
          // But this will only work for first page unless
          // we also increase i for what page we are on.
          await this.next_page();
          i = 0

        }
        this.current_file = this.file_list[i]
        this.$emit('file_changed', this.current_file)
      }
      else{
        this.current_file = file;
        this.$emit('file_changed', this.current_file)
      }


    },
    change_file_request(file) {
      if (this.control_key_down == true) {
        this.select_from_something(file)
        return
      }

      this.change_file('change_file', file)
    },

    item_changed() {

    },
    request_media() {
      this.select_from_metadata = false
      this.selected = []

      this.get_media();
    },
    async next_page() {
      this.page_number += 1
      await this.get_media();
    },
    async previous_page() {
      /* TODO  trying to follow prior design but this isn't great
       * prefer to share this function...
       *
       */
      this.page_number -= 1
      await this.get_media();

    },
    remove_function: function (file) {

      this.selected = [file]

      this.api_file_update('REMOVE')

      // handled by api_file_update() so not needed
      // but this may have been cleaner way to do it for single file
      // this.$emit('remove_file_request', file)

    },
    annotation_example_toggle_function(image, index) {

      axios.post('/api/project/' + this.$props.project_string_id
        + '/images/annotation_example_toggle',
        { image: image })
        .then(response => {
          if (response.data.success = true) {

            this.$emit('annotation_example_image_toggle_ui', index)

          }
        }).catch(e => { console.error(e) })
    },

    get_video_single_detail(video_id) {
      axios.get('/api/project/' + this.$props.project_string_id
        + '/video/single/' + video_id + '/view')
        .then(response => {
          if (response.data.success = true) {


            this.current_video = response.data.video
            this.$emit('current_video_update', this.current_video)

          }
        }).catch(e => { console.error(e) })

    },

    inference_selected() {

      this.inference_selected_loading = true
      this.error_inference = {}

      axios.post('/api/walrus/project/' + this.$props.project_string_id
            + '/inference/add',
        {
          'file_list' : this.selected
        })
        .then(response => {
          if (response.data.log.success = true) {
            this.run_FAN_success = true
          }

          this.inference_selected_loading = false

        }).catch(error => {
          console.error(error)
          this.inference_selected_loading = false
          if (error.response.status == 400) {
              this.error_inference = error.response.data.log.error
          }

        })

    },

    api_file_update(mode) {

      this.api_file_update_loading = true
      this.info = {}  // reset

      axios.post('/api/v1/project/' + this.$props.project_string_id
              + '/file/update',
        {
          directory_id: this.$store.state.project.current_directory.directory_id,
          file_list: this.selected,
          mode: mode,
          select_from_metadata: this.select_from_metadata,
          cascade_archive_tasks: this.cascade_archive_tasks,
          metadata_proposed: this.metadata_previous

        })
        .then(response => {


          this.request_media()
          this.info = response.data.log.info
          this.selected = []    // reset

          this.api_file_update_loading = false
          this.cascade_archive_tasks = false

        }).catch(e => {
          console.error(e)
          this.api_file_update_loading = false

        })

  },
    add_to_inference(file) {

      //  TODO I think this method is deprecated??

      axios.post('/api/project/' + this.$props.project_string_id
        + '/file/' + file.id
        + '/inference/add',
        {})
        .then(response => {
          if (response.data.success = true) {
            //this.run_FAN_success = true
          }

          // Until we have better system
          //this.run_FAN_disabled = false
        }).catch(e => {
          console.error(e)
          this.run_FAN_disabled = false
        })

    }

  }
}

) </script>
