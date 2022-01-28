<template>
  <div v-cloak class="job_list_container">
    <main_menu style="border-bottom: 1px solid #e1e4e8" height="130px">
      <template slot="second_row">

        <v-toolbar
          dense
          elevation="0"
          fixed
          style="width: 100%;"
          height="30px"
        >

          <v-progress-linear
            :active="loading"
            :indeterminate="loading"
            absolute
            bottom
            color="primary accent-4"
          ></v-progress-linear>

          <bread_crumbs
            :item_list=bread_crumb_list>

          </bread_crumbs>


        </v-toolbar>

      </template>


      <template slot="third_row">
        <v-toolbar fixed
                   height="50px"
                   elevation="0">


          <v-toolbar-items class="pt-2">
            <tooltip_button
              datacy='new_tasks'
              tooltip_message="New Tasks"
              icon="add"
              :bottom="true"
              v-if="$store.state.builder_or_trainer.mode == 'builder'"
              :disabled="!project_string"
              color="primary"
              :icon_style="true"
              :large="true"
              :href="'/project/' + project_string + '/job/new'"
              @click="$router.push('/project/' + project_string + '/job/new')">
            </tooltip_button>

            <tooltip_button
              tooltip_message="Project Job Pipelines"
              icon="mdi-file-tree-outline"
              :text_style="false"
              :bottom="true"
              v-if="$store.state.builder_or_trainer.mode == 'builder'"
              :disabled="!project_string"
              :icon_style="true"
              color="primary"
              @click="open_pipelines_dialog"
            >
            </tooltip_button>
            <tooltip_button
              tooltip_message="Job Launches Log"
              icon="list"
              :text_style="false"
              :bottom="true"
              v-if="$store.state.builder_or_trainer.mode == 'builder'"
              :disabled="!project_string"
              :icon_style="true"
              color="primary"
              @click="$router.push('/job/launches')"
            >
            </tooltip_button>

            <v_job_cancel :job_list="selected"
                          @cancel_job_success="job_list_api"
            >
            </v_job_cancel>

            <tooltip_button
              tooltip_message="Generate Samples"
              @click="open_confirm_dialog_sample_data"
              icon="mdi-apps-box"
              :bottom="true"
              :loading="loading_create_sample_data"
              color="primary"
              :icon_style="true">
            </tooltip_button>

            <tooltip_button
              tooltip_message="Refresh"
              icon="refresh"
              :text_style="false"
              :bottom="true"
              :disabled="loading"
              :loading="loading"
              :icon_style="true"
              color="primary"
              @click="job_list_api"
            >
            </tooltip_button>

          </v-toolbar-items>

          <!-- Enterprise feature -->
          <!--
            <project_org_select
              class="ml-4"
              v-if="$store.state.builder_or_trainer.mode == 'builder'"
              v-model="share_type"
              label="Share type"
              :disabled="loading">
            </project_org_select>
          -->

          <v-toolbar-items class="pt-4 pl-4 pr-4">

            <v-text-field v-model="text_search"
                          @input="search_jobs"
                          label="Search"
                          clearable>

            </v-text-field>

            <job_status_select
              class="ml-4"
              v-model="status"
              label="Status"
              @change="search_jobs"
              :disabled="loading || $store.state.builder_or_trainer.mode == 'trainer'"
            >
            </job_status_select>


            <job_type_select
              class="ml-4"
              v-model="type"
              label="Normal or Exam"
              @change="search_jobs"
              :disabled="loading">
            </job_type_select>

            <!-- WIP Feature-->
            <!--
              <v-select
                class="ml-4"
                        :items="instance_type_list"
                        v-model="instance_type"
                        label="Instance type"
                        item-value="text"
                        :disabled="loading"
                        @change="">
              </v-select>
            -->

            <member_select
              style="max-width: 18%;"
              class="ml-4"
              v-model="selected_member_list_ids"
              :member_list="project_member_list"
              :show_names_on_selected="false"
              :multiple="true"
            >
            </member_select>

            <v-checkbox v-model="my_jobs_only"
                        label="My Jobs Only">
            </v-checkbox>


            <!-- Future release -->
            <!--
        # TODO Credential requirements
        (ie option to show Exams if don't yet have credential?')
        -->
          </v-toolbar-items>

        </v-toolbar>
      </template>

    </main_menu>

    <v-alert v-if="!loading && Job_list.length == 0"
             type="info"
    >

      Welcome! Click the plus button to create your first batch of Tasks. (No Results Found.)


      <!-- TODO use new standard button style
        and link to new docs once created -->

      <!--
      <v-btn v-if="$store.state.builder_or_trainer.mode == 'builder'"
            color="white darken-2"
            href="https://diffgram.readme.io/reference#job_new"
            target="_blank"
            >
      <v-icon left>mdi-book</v-icon>
      Job Docs
    </v-btn>
    -->

    </v-alert>

    <v-alert type="info"
             :value="
               $store.state.builder_or_trainer.mode == 'trainer'"
    >
    </v-alert>
    <!-- Case of deferred launch ie for large jobs -->
    <v-alert id="success_launch"
             type="success"
             dismissible
             v-if="success_launch">
      Launching! Tasks will populate over time. See Launch Log for more info.
    </v-alert>

    <v-layout class="d-flex flex-column">
      <div class="d-flex align-center mt-1" >
        <div style="border: 1px solid #e1e4e8" class="d-flex">
          <tooltip_button
            style="border-right: 1px solid #e1e4e8"
            tooltip_message="Cards View"
            @click="set_view_mode('cards')"
            icon="mdi-view-grid-plus"
            :icon_style="true"
            value="card"
            :color="view_mode === 'cards' ? 'secondary' : undefined"
            :bottom="true"
          >
          </tooltip_button>

          <tooltip_button
            tooltip_message="Table View"
            @click="set_view_mode('table')"
            icon="mdi-table"
            :icon_style="true"
            value="table"
            :color="view_mode === 'table' ? 'secondary' : undefined"
            :bottom="true"
          >
          </tooltip_button>
        </div>


      </div>
      <job_list_card_display
        v-if="view_mode === 'cards'"
        :project_string_id="project_string"
        :loading="loading"
        :job_list="Job_list"></job_list_card_display>

      <v-data-table :headers="headers_view"
                    v-if="view_mode === 'table'"
                    :loading="loading"
                    :items="Job_list"
                    item-key="id"
                    v-model="selected"
                    show-select
                    ref="job_list_table">

        <!-- appears to have to be item for vuetify syntax-->
        <template slot="item"
                  slot-scope="props">

          <tr>

            <td>
              <v-checkbox v-model="props.isSelected"
                          @change="props.select($event)"
                          primary>
              </v-checkbox>
            </td>

            <td>
              <v-btn color="primary"
                     text
                     @click="job_detail(props.item)">
                <div v-if="props.item.name">
                  {{props.item.name.slice(0, 40)}}
                  <div v-if="props.item.name.length >= 40">
                    ...
                  </div>
                </div>
              </v-btn>
            </td>

            <td>
              <!-- start Status -->

              <v-layout>

                <tooltip_icon
                  tooltip_message="Active"
                  v-if="props.item.status == 'active'"
                  icon="mdi-inbox"
                  color="green">
                </tooltip_icon>

                <tooltip_icon
                  tooltip_message="Cancelled"
                  v-if="props.item.status == 'cancelled'"
                  icon="mdi-cancel"
                  color="red">
                </tooltip_icon>

                <tooltip_icon
                  tooltip_message="Draft"
                  v-if="props.item.status == 'draft'"
                  icon="mdi-file"
                  color="orange">
                </tooltip_icon>

                <tooltip_icon
                  tooltip_message="Complete"
                  v-if="props.item.status == 'complete'"
                  icon="mdi-check"
                  color="gray">
                </tooltip_icon>

                <tooltip_icon
                  tooltip_message="Failed"
                  v-if="props.item.status == 'failed'"
                  icon="mdi-alert-circle"
                  color="error">
                </tooltip_icon>

                <tooltip_icon
                  :tooltip_message="'Requested Launch: ' +
                              props.item.launch_datetime | moment('ddd, MMM Do H:mm a')"
                  v-if="props.item.waiting_to_be_launched"
                  icon="mdi-rocket"
                  color="blue">
                </tooltip_icon>


              </v-layout>

              <!-- end Status -->
            </td>

            <td>

              <label_select_only
                v-if="props.item.label_dict &&
                      props.item.label_dict.label_file_list_serialized"
                :mode=" 'multiple' "
                :label_prompt="null"
                :view_only_mode="true"
                :label_file_list_prop="props.item.label_dict.label_file_list_serialized"
                :load_selected_id_list="props.item.label_dict.label_file_list"
                :limit="3"
              >
              </label_select_only>

            </td>

            <td>
              <!--
              <member_select
                  v-if="props.item.member_list_ids"
                  v-model="props.item.member_list_ids"
                  :member_list="$store.state.project.current.member_list"
                  :multiple="true"
                  :view_only="true"
                             >
              </member_select>
             -->

              <member_inline_view
                :member_list_ids="props.item.member_list_ids">
              </member_inline_view>

            </td>


            <td>
              <!-- start TYPE -->
              <job_type :type="props.item.type">
              </job_type>

            </td> <!-- end TYPE -->

            <td>
              <div style="max-width: 200px" class="d-flex flex-wrap"
                   v-if="props && props.item && props.item.attached_directories_dict && props.item.attached_directories_dict.attached_directories_list">
                <div class="dir d-flex align-center  justify-center ml-1"
                     v-for="dir in props.item.attached_directories_dict.attached_directories_list">
                  <v-icon color="primary">mdi-folder</v-icon>
                  <p class="ma-0">{{ dir.nickname }}</p>
                </div>

              </div>
            </td>
            <td>
              <div style="max-width: 200px" class="d-flex flex-wrap"
                   v-if="props && props.item && props.item.completion_directory">
                <div class="dir d-flex align-center  justify-center" v-if="props.item.completion_directory.nickname">
                  <v-icon color="primary">mdi-folder</v-icon>
                  <p class="ma-0">{{ props.item.completion_directory.nickname }}</p>
                </div>
              </div>
            </td>

            <td>
              <icon_from_regular_list
                v-if="props.item.interface_connection"
                :item_list="$store.state.connection.integration_spec_list"
                :value="props.item.interface_connection.integration_name"
              >
              </icon_from_regular_list>
              <!-- Default case,. hard code value to diffgram
                   because we currently aren't store Diffgram as a "connection"
                -->
              <icon_from_regular_list
                v-if="!props.item.interface_connection"
                :item_list="$store.state.connection.integration_spec_list"
                value="diffgram"
              >
              </icon_from_regular_list>
            </td>

            <td>

              <!-- Would be nice for this to be it's own component
                but not clear what this would be shared with
                ie maybe should be part of annotation...

                Either way need a new series here...
                and current instance detail thing I think just does
                icon without tooltip...
                -->

              <tooltip_icon
                tooltip_message="Box"
                v-if="props.item.instance_type =='box'"
                icon="mdi-checkbox-blank"
                color="green lighten-1">
              </tooltip_icon>


              <tooltip_icon
                tooltip_message="Polygon"
                v-if="props.item.instance_type =='polygon'"
                icon="mdi-vector-polygon"
                color="green lighten-1">
              </tooltip_icon>

              <tooltip_icon
                tooltip_message="Tag"
                v-if="props.item.instance_type =='tag'"
                icon="mdi-tag"
                color="green lighten-1">
              </tooltip_icon>

            </td>

            <td>

              {{ props.item.time_updated | moment("ddd, MMM Do H:mm a") }}

            </td>

            <td>
              {{ props.item.stat_count_complete}}
            </td>

            <td>
              {{ props.item.stat_count_available}}
            </td>

            <td>
              {{ props.item.file_count_statistic }}
            </td>

            <td>
              <v-layout row>

                <v-btn color="primary"
                       @click="job_detail(props.item)">
                  View
                </v-btn>

                <!--
                 Strange issues with how it re renders error message when the list updates
                -->
                <!--
            <v_job_cancel :job="props.item"
                          @cancel_job_success="job_list_api()">
            </v_job_cancel>
            -->
              </v-layout>
            </td>

          </tr>
        </template>
        <div v-if="!loading">
          <v-alert slot="no-data" color="error" icon="warning">
            No results found.
          </v-alert>
        </div>


      </v-data-table>
    </v-layout>


    <v-dialog v-model="dialog_confirm_sample_data" max-width="450px">
      <v-card>
        <v-card-title class="headline">
          Create sample data
        </v-card-title>
        <v-card-text>
          Do you want to create sample task templates?
          This will add task templates to the project
          <v-select
            label="Select Structure"
            :items="structures_list"
            item-text="name"
            item-value="value"
            v-model="structure"
          ></v-select>
        </v-card-text>
        <v_error_multiple :error="error_sample_data">
        </v_error_multiple>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="primary darken-1"
            text
            @click="dialog_confirm_sample_data = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="success darken-1"
            text
            :loading="loading_create_sample_data"
            @click="create_sample_task_template"
          >
            Create Sample Data
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-snackbar
      v-model="snackbar_success"
      :timeout="3000"
      color="primary"
    >
      Sample data created successfully.
      <template v-slot:action="{ attrs }">
        <v-btn
          color="white"
          text
          v-bind="attrs"
          @click="snackbar_success = false">
          Close
        </v-btn>
      </template>
    </v-snackbar>
    <project_pipelines_dialog ref="project_pipelines_dialog"
                              :job_list="Job_list"
                              :project_string_id="project_string">

    </project_pipelines_dialog>
  </div>
</template>

<script lang="ts">
  import {debounce} from "debounce";
  import axios from 'axios';
  import job_type from './job_type';
  import job_type_select from '../../regular_concrete/job_type_select'
  import project_pipelines_dialog from '../../project/project_pipelines_dialog'
  import job_list_card_display from '../job/job_list_card_display'
  import label_select_only from '../../label/label_select_only.vue'

  import Vue from "vue";
  import {create_event} from "../../event/create_event";

  export default Vue.extend({
      name: 'job_list',

      components: {
        job_type,
        job_type_select,
        project_pipelines_dialog,
        job_list_card_display,
        label_select_only
      },

      props: {

        // TODO clarify why we have this prop here
        // since using Vuex store for job_list below
        'project_string_id': {
          default: null
        }

      },
      watch: {
        '$route': 'mount'
      },
      data() {
        return {
          selected_member_list_ids: [],
          success_launch: null,
          text_search: undefined,
          view_mode: 'cards',

          selected: [],

          options: {
            'sortBy': ['column5'],
            'sortDesc': [true],
            'itemsPerPage': 25
          },

          Job_list: [],

          org_list: ["None"],
          org: "None",    // Continue theme / notes on back end this must be string
          // "None" and not null for current back end setup

          loading: false,
          inference_selected_loading: false,
          dialog_confirm_sample_data: false,
          loading_create_sample_data: false,
          snackbar_success: false,

          my_jobs_only: false,

          share_type: "project",

          status_list: ["All", "draft", "active", "complete", "cancelled"],
          status: 'All',

          field_list: ['Self Driving', 'Medical', 'Construction', 'Other', 'All'],
          field: 'All',
          structure: '1_pass',
          structures_list: [
            {name: '1 Stage', value: '1_pass'},
            {name: 'Multi-Stage (2 Stages)', value: '2_pass'},
            {name: '2 Input Datasets, 1 Output', value: '2_input_1_output'}
          ],
          // maybe hide for now?
          category_list: ['Computer vision'],
          category: 'Computer vision',

          type_list: ['All', 'Normal', 'Exam'],  // 'Learning'
          type: 'Normal',

          instance_type_list: ['All', 'polygon', 'box', 'tag'],
          instance_type: 'All',

          metadata_limit_options: [10, 25, 100, 250],
          metadata_limit: 10,
          error_sample_data: {},

          request_next_page_flag: false,
          request_next_page_available: true,

          instance_changes: [],

          current_video: {
            id: null
          },

          headers_builder: [
            {
              text: "Name",
              align: 'left',
              sortable: true,
              value: 'name'
            },
            {
              text: "Status",
              align: 'left',
              sortable: true,
              value: 'status'
            },
            {
              text: "Schema",
              align: 'left',
              sortable: false,
              width: '500px'
            },
            {
              text: "Users",
              align: 'left',
              sortable: true,
              value: 'member_list_ids'
            },
            {
              text: "Type",
              align: 'left',
              sortable: true,
              value: 'type'
            },
            {
              text: "Incoming Datasets",
              align: 'left',
              sortable: true,
              value: 'attached_directories_dict.attached_directories_list'
            },
            {
              text: "Outgoing Dataset",
              align: 'left',
              sortable: true,
              value: 'type'
            },
            {
              text: "Interface",
              align: 'left',
              sortable: true,
              value: "interface_connection.integration_name"
            },
            {
              text: "Instance",
              align: 'left',
              sortable: true,
              value: "instance_type"
            },
            {
              text: "Last Updated",
              align: 'left',
              sortable: true,
              value: "time_updated"
            },
            {
              text: "Tasks Complete",
              align: 'left',
              sortable: true,
              value: "stat_count_complete"
            },
            {
              text: "Tasks Available",
              align: 'left',
              sortable: true,
              value: "stat_count_available"
            },
            {
              text: "Files",
              align: 'left',
              sortable: true,
              value: "file_count_statistic"
            },
            {
              text: "Actions",
              align: 'left',
              sortable: false
            }
          ],
          headers_trainer: [
            {
              text: "Name",
              align: 'left',
              sortable: true,
              value: 'name'
            },
            {
              text: "Status",
              align: 'left',
              sortable: true,
              value: 'status'
            },
            {
              text: "Type",
              align: 'left',
              sortable: true,
              value: 'type'
            },
            {
              text: "Total",
              align: 'left',
              sortable: true,
              value: "stat_count_complete"
            },
            {
              text: "Available",
              align: 'left',
              sortable: true,
              value: "stat_count_available"
            },
            {
              text: "Actions",
              align: 'left',
              sortable: false
            }
          ]

        }
      },
      computed: {
        project_string: function () {
          if (this.$props.project_string_id) {
            return this.$props.project_string_id;
          } else {
            return this.$store.state.project.current.project_string_id
          }
        },
        project_member_list: function () {
          return this.$store.state.project.current.member_list
        },
        bread_crumb_list: function () {
          return [
            {
              text: 'Tasks',
              disabled: true
            }
          ]
        },

        headers_view: function () {

          // Not sure if want to use vuex directly here
          // Or local variable instead
          // Since changing modes would effect other stuff

          if (this.$store.state.builder_or_trainer.mode == "trainer") {
            return this.headers_trainer
          }
          if (this.$store.state.builder_or_trainer.mode == "builder") {
            return this.headers_builder
          }


        },

        metadata: function () {

          let project_string_id = this.project_string;

          return {
            'my_jobs_only': this.my_jobs_only,
            'limit': this.metadata_limit,
            'request_next_page': this.request_next_page_flag,
            'previous': this.metadata_previous,
            'builder_or_trainer': this.$store.state.builder_or_trainer,
            'field': this.field,
            'search': this.text_search === '' ? undefined : this.text_search,
            'category': this.category,
            'type': this.type,
            'status': this.status,
            'members': this.selected_member_list_ids,
            'instance_type': this.instance_type,
            'project_string_id': project_string_id,
            'org': this.org,
            'share_type': this.share_type
          }

        }

      },

      created() {

      },

      mounted() {
        this.add_visit_history_event();
        this.mount()

        /*
        var self = this
        this.$store.watch((state) => { return this.$store.state.media.refresh },
          (new_val, old_val) => {
            self.request_media()
          },
        )
        */

        // Set default org if it exists
        if (this.$store.state.org.current) {
          this.org_list.push(this.$store.state.org.current.name)
          this.org = this.$store.state.org.current.name
        }

        if (this.$store.state.builder_or_trainer.mode == 'trainer') {
          this.share_type = "Market"
        }

      },
      methods: {
        set_view_mode: function (new_mode) {
          this.view_mode = new_mode;
        },

        add_visit_history_event: async function () {
          const event_data = await create_event(this.project_string, {
            page_name: 'job_list',
            object_type: 'page',
            user_visit: 'user_visit',
          })
        },

        open_pipelines_dialog: function () {
          this.$refs.project_pipelines_dialog.open();
        },
        create_sample_task_template: async function () {
          this.loading_create_sample_data = true;
          try {
            const response = await axios.post('/api/walrus/v1/project/' + this.$store.state.project.current.project_string_id + '/gen-data', {
              data_type: 'task_template',
              structure: this.structure
            })
            if (response.status === 200) {
              this.request_refresh = Date.now();
              this.dialog_confirm_sample_data = false;
              this.snackbar_success = true;
              this.job_list_api();
            }
          } catch (error) {
            this.error_sample_data = this.$route_api_errors(error);
          } finally {
            this.loading_create_sample_data = false;
          }
        },
        open_confirm_dialog_sample_data: function () {
          this.dialog_confirm_sample_data = true;
        },
        mount() {
          this.job_list_api()
        },

        item_changed() {
          this.request_next_page_available = false
        },
        search_jobs: debounce(async function () {
          this.job_list_api();
        }, 200),
        job_list_api() {

          this.loading = true

          // refresh query paremeters
          this.my_jobs_only = (this.$route.query["my_jobs_only"] === 'true')

          if (this.success_launch == true) {  // hacky reset, maybe prefer to update query param
            this.success_launch = false
          } else if (this.success_launch == null) {
            // because when it transitions it doesn't seem to grab this properly (was in created())
            this.success_launch = (this.$route.query["success_launch"] == 'true')
          }

          axios.post('/api/v1/job/list', {

            'metadata': this.metadata

          }).then(response => {

            if (response.data['Job_list'] != null) {

              this.Job_list = response.data['Job_list']
              this.metadata_previous = response.data['metadata']
            }

            this.loading = false

          })
            .catch(error => {
              console.error(error);
              this.loading = false
              this.logout()
            });
        },

        job_detail(job) {

          this.$router.push("/job/" + job.id)

          if (job.status == "draft") {
            this.$router.push("/job/new/" + job.id)
          }

        },

        remove_function: function (file) {


        }

      }
    }
  ) </script>
<style>
  .job_list_container {
    padding: 0.5rem 2rem;
  }

  .v-data-table__wrapper {
    overflow: visible;
  }

  html {
    overflow: auto;
  }
</style>
