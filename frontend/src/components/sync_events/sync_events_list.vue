<template>
  <div v-cloak class="sync-events-container">
    <v-card>
      <main_menu>
      </main_menu>
      <h1 class="pl-4 pt-4" ><v-icon color="primary" size="48">mdi-sync</v-icon>Sync Events</h1>
      <v-layout class="d-flex justify-start pl-8 pb-4 pr-8 align-center" style="width: 100%;">
        <v-row>
          <v-col cols="1" class="d-flex align-center">  <v-btn color="primary" @click="refresh_list" icon><v-icon>mdi-sync</v-icon></v-btn></v-col>
          <v-col cols="2" class="d-flex">
            <v-icon color="primary" class="mr-4">mdi-filter</v-icon>
            <v_directory_list class="pt-2"
                              :project_string_id="project_string_id"
                              :show_new="false"
                              label="Source"
                              :initial_dir_from_state="false"
                              :update_from_state="false"
                              :set_current_dir_on_change="false"
                              :change_on_mount="false"
                              :show_update="false"
                              :clearable="true"
                              @change_directory="change_source_dataset">
            </v_directory_list>
          </v-col>
          <v-col cols="2">
            <v_directory_list class="pt-2"
                              :project_string_id="project_string_id"
                              :show_new="false"
                              label="Destinations"
                              :initial_dir_from_state="false"
                              :update_from_state="false"
                              :set_current_dir_on_change="false"
                              :change_on_mount="false"
                              :show_update="false"
                              :clearable="true"
                              @change_directory="change_destination_dataset">
            </v_directory_list>
          </v-col>
          <v-col cols="2" class="pt-5">
            <diffgram_select
              :item_list="status_list"
              v-model="status"
              label="Status"
              item-value="value"
              :return_object="true"
              :disabled="loading"
              :clearable="true"
              @change="status_changed"
            >

            </diffgram_select>
          </v-col>
          <v-col cols="2" class="pt-5">
            <job_select
              v-model="job"
              label="Job"
            >
            </job_select>
          </v-col>
          <v-col cols="3" class="pt-5">
            <date_picker
              @date="date = $event"
              :with_spacer="false"
              :initialize_empty="true"
            >
            </date_picker>
          </v-col>
        </v-row>
      </v-layout>
      <v-data-table :headers="headers"
                    :items="sync_events_list"
                    :loading="loading"
                    class="elevation-1  pl-8 pr-8"
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
              {{ props.item.id }}
            </td>
            <td>
              <div v-if="props.item.created_date">
                {{props.item.created_date}}
              </div>
              <div v-else>
                N/A
              </div>
            </td>

            <td>

              <div style="max-width: 200px" class="d-flex flex-wrap"
                   v-if="props && props.item && props.item.dataset_source">
                <div class="dir d-flex align-center  justify-center ml-1">
                  <v-icon color="primary">mdi-folder</v-icon>
                  <p class="ma-0">{{ props.item.dataset_source.nickname }}</p>
                </div>

              </div>
            </td>

            <td>
              <div style="max-width: 200px" class="d-flex flex-wrap"
                   v-if="props && props.item && props.item.dataset_destination">
                <div class="dir d-flex align-center  justify-center ml-1">
                  <v-icon color="primary">mdi-folder</v-icon>
                  <p class="ma-0">{{ props.item.dataset_destination.nickname }}</p>
                </div>

              </div>
            </td>

            <td>
              <v-layout>
                <tooltip_icon
                  tooltip_message="Initialized"
                  v-if="props.item.status == 'init'"
                  icon="mdi-sync"
                  color="gray">
                </tooltip_icon>

                <tooltip_icon
                  tooltip_message="Failed"
                  v-if="props.item.status == 'failed'"
                  icon="mdi-cancel"
                  color="red">
                </tooltip_icon>

                <tooltip_icon
                  tooltip_message="Completed"
                  v-if="props.item.status == 'completed'"
                  icon="mdi-check"
                  color="green">
                </tooltip_icon>
              </v-layout>
            </td>
            <td>
              <div v-if="props.item.event_trigger_type">
                {{props.item.event_trigger_type}}
              </div>
              <div v-else>
                N/A
              </div>
            </td>
            <td>
              <div v-if="props.item.event_effect_type">
                {{props.item.event_effect_type}}
              </div>
              <div v-else>
                N/A
              </div>
            </td>
            <td>
              <div v-if="props.item.description">
                {{props.item.description}}
              </div>
              <div v-else>
                N/A
              </div>
            </td>
            <td>
              <div v-if="props.item.file && props.item.event_effect_type !== 'create_task'">
                <a :href="`/file/${props.item.file.id}`">  {{props.item.file.original_filename}}</a>

              </div>
              <div v-else>
                N/A
              </div>
            </td>
            <td>
              <div v-if="props.item.job">
                <a :href="`/job/${props.item.job.id}`">{{props.item.job.name}}</a>
              </div>
              <div v-else>
                N/A
              </div>
            </td>
            <td>
              <div v-if="props.item.created_task_id">

                <a :href="`/task/${props.item.created_task_id}`">TASK ID: {{props.item.created_task_id}}</a>
              </div>
              <div v-else>
                N/A
              </div>
            </td>
            <td>
              <div v-if="props.item.completed_task_id">

                <a :href="`/task/${props.item.completed_task_id}`"> TASK ID: {{props.item.completed_task_id}}</a>
              </div>

              <div v-else>
                N/A
              </div>
            </td>
          </tr>
        </template>
        <div v-if="!loading">
          <v-alert slot="no-data" color="error" icon="warning">
            No results found.
          </v-alert>
        </div>


      </v-data-table>


    </v-card>

  </div>
</template>

<script lang="ts">

  import axios from '../../services/customInstance';
  import Vue from "vue";
  import diffgram_select from '../../components/regular/diffgram_select'
  import {create_event} from "../event/create_event";

  export default Vue.extend({
      name: 'sync_events_list',

      components: {
        diffgram_select: diffgram_select
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

          selected: [],
          source_dataset: undefined,
          destination_dataset: undefined,
          job: undefined,
          date: undefined,
          status: undefined,
          status_list:[
            {'name': 'Completed', 'value': 'completed', 'icon': 'mdi-check'},
            {'name': 'In Progress', 'value': 'init', 'icon': 'mdi-sync'},
            {'name': 'Failed', 'value': 'failed', 'icon': 'mdi-cancel'},
          ],
          options: {
            'sortBy': ['column5'],
            'sortDesc': [true],
            'itemsPerPage': 25
          },

          sync_events_list: [],

          org_list: ["None"],
          org: "None",    // Continue theme / notes on back end this must be string
          // "None" and not null for current back end setup

          loading: false,
          inference_selected_loading: false,


          share_type: "project",

          headers: [
            {
              text: "ID",
              align: 'left',
              sortable: false,
              value: 'id'
            },
            {
              text: "Created Date",
              align: 'left',
              sortable: false,
              value: 'created_date'
            },
            {
              text: "Dataset Source",
              align: 'left',
              sortable: false,
              value: 'dataset_source'
            },
            {
              text: "Dataset Destination",
              align: 'left',
              sortable: false,
              value: 'dataset_destination'
            },
            {
              text: "Status",
              align: 'left',
              sortable: false,
              value: "status"
            },
            {
              text: "Triggered By",
              align: 'left',
              sortable: false,
              value: 'event_trigger_type'
            },
            {
              text: "Effect caused",
              align: 'left',
              sortable: false,
              value: 'event_effect_type'
            },
            {
              text: "Description",
              align: 'left',
              value: 'description'
            },
            {
              text: "File",
              align: 'left',
              sortable: false,
              value: 'file'
            },
            {
              text: "Job",
              align: 'left',
              sortable: false,
              value: 'job'
            },
            {
              text: "Created Task from Event",
              align: 'left',
              sortable: false,
              value: "created_task"
            },
            {
              text: "Completed Task from Event",
              align: 'left',
              sortable: false,
              value: "completed_task"
            },
          ],

        }
      },
      computed: {

        bread_crumb_list: function () {
          return [
            {
              text: 'Sync Events',
              disabled: true
            }
          ]
        },
        project_string_id: function(){
          let project_string_id = null
          if (this.$route.query.project_id) {
            project_string_id = this.$route.query.project_id
          }
          else{
            // Fallback to current project if no query param is provided.
            project_string_id = this.$store.state.project.current.project_string_id;
          }
          return project_string_id;
        },
        metadata: function () {

          let project_string_id = null
          if (this.$route.query.project_id) {
            project_string_id = this.$route.query.project_id
          }
          else{
            // Fallback to current project if no query param is provided.
            project_string_id = this.$store.state.project.current.project_string_id;
          }

          return {
            project_string_id: project_string_id,
            job_id: this.job ? this.job.id : undefined,
            status: this.status ? this.status.value : undefined,
            dataset_destination_id: this.destination_dataset ? this.destination_dataset.directory_id : undefined,
            dataset_source_id: this.source_dataset ? this.source_dataset.directory_id : undefined,
            date_from: this.date ? this.date.from : undefined,
            date_to: this.date ? this.date.to : undefined

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
        add_visit_history_event: async function(){
          const event_data = await create_event(this.project_string_id, {
            page_name: 'sync_events_list',
            object_type: 'page',
            user_visit: 'user_visit',
          })
        },
        change_source_dataset: function(dataset){
          this.source_dataset = dataset
        },
        change_destination_dataset: function(dataset){
          this.destination_dataset = dataset;
        },
        mount() {
          this.sync_event_list_api()
        },

        item_changed() {
          this.request_next_page_available = false
        },
        status_changed(){

        },
        refresh_list: async function(){
          await this.sync_event_list_api();
        },
        async sync_event_list_api() {
          this.loading = true
          try {
            const response = await axios.post('/api/v1/sync-events/list', {
              'metadata': this.metadata
            })
            if (response.data.sync_events_list) {
              this.sync_events_list = response.data.sync_events_list
            }
          } catch (error) {
            console.error(error);

          } finally {
            this.loading = false;
          }
        },


      }
    }
  ) </script>
<style scoped>
  .sync-events-container{
    padding: 2rem 2rem;
  }
</style>
