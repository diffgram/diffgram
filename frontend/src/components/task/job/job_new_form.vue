<template>
  <v-container class="ma-0">
    <v-row>
      <v-col cols="12">

        <v-card-title> Setup </v-card-title>

        <v-text-field label="Name"
                      data-cy="name-input"
                      v-model="job.name">
        </v-text-field>

        <v-container fluid class="d-flex align-top">

          <div class="pr-4">
            <tooltip_button
                tooltip_message="Quick Edit Project Level Schema"
                @click="open_labels_dialog"
                icon="mdi-format-paint"
                :icon_style="true"
                :large="true"
                color="primary">
            </tooltip_button>
          </div>

          <label_select_only
            :project_string_id="project_string_id"
            label_prompt="Schema Selected For Tasks"
            :mode=" 'multiple' "
            data-cy="label-select"
            @label_file="receive_label_file($event)"
            :load_selected_id_list="job.label_file_list"
            :select_all_at_load="true"
            ref="label_select"

          >
          </label_select_only>

        </v-container>

        <v-card-title> Optional </v-card-title>

        <!-- User Select -->
        <member_select
            v-model="job.member_list_ids"
            label="Select Specific Users"
            :member_list="$store.state.project.current.member_list"
            :multiple="true"
            :initial_value="job_id ? job.member_list_ids : ['all']"
            :allow_all_option="true"
                       >
        </member_select>

        <!-- Assumption here is that for actual tasks a data engineer / project admin
          will use a specific single script. In the future this could be expanded to a set
          of options (and even then there still could be a defualt.-->

        <userscript_select
            :project_string_id="project_string_id"
            @change="job.default_userscript_id = $event.id"
            label="Choose a Default Userscript"
                           >
        </userscript_select>

        <connection_select
          :hide_if_empty="true"
          :project_string_id="project_string_id"
          v-model="job.interface_connection"
          :show_new="true"
          :add_diffgram_default_option="true"
          :start_empty="true"
          label="Choose a Interface Provider"
          :features_filters="{labeling_interface:true}"
          data-cy="connection-select"
        >
        </connection_select>

        <!-- OpenCore- Hide while WIP -->
        <!--
        <v-layout>
          <v-checkbox label="Use Pro Network"
                      v-model="job.pro_network"
          >
          </v-checkbox>

          <a class="pa-4"
             href="https://diffgram.readme.io/docs/create-tasks-for-pro-network"
             target="_blank">
              Learn More About the Pro Network
          </a>
        </v-layout>
        -->

        <div v-if="quick_create">
          <v-expansion-panels accordion
                              flat>
          <v-expansion-panel
          >
            <v-expansion-panel-header>More Options</v-expansion-panel-header>
            <v-expansion-panel-content>

              <v-select :items="instance_type_list"
                        v-model="job.instance_type"
                        label="Instance type"
                        ref="instance_type"
                        data-cy="instance-type-select"
                        item-value="text"
                        :disabled="loading"
                        @change="">
              </v-select>

              <v-select :items="share_list"
                        v-model="job.share_object"
                        data-cy="share-select"
                        label="Share"
                        item-text="text"
                        return-object
                        :disabled="loading">
              </v-select>

              <v-select :items="type_list"
                        v-model="job.type"
                        data-cy="type-select"
                        label="Type"
                        item-value="text"
                        :disabled="loading">
              </v-select>

              <diffgram_select
                :item_list="file_handling_list"
                data-cy="file-handling-select"
                v-model="job.file_handling"
                label="File Handling"
                :disabled="loading"
              >
              </diffgram_select>

              <!--
              <div v-if="$store.state.user.current.is_super_admin == true">
                <v-checkbox label="td_api_trainer_basic_training"
                            v-model="job.td_api_trainer_basic_training"
                >
                </v-checkbox>
              </div>
              -->

              <div v-if="['External', 'Shared'].includes(job.share)">
              </div>


              <v-expansion-panels>
                <v-expansion-panel>
                  <div slot="header">Advanced</div>
                  <v-expansion-panel-content>
                    <v-select :items="review_by_human_frequency_list"
                              v-model="job.review_by_human_freqeuncy"
                              label="Review freqeuncy"
                              item-value="text"
                              :disabled="loading">
                    </v-select>

                  </v-expansion-panel-content>
                </v-expansion-panel>
              </v-expansion-panels>
            </v-expansion-panel-content>
          </v-expansion-panel>
          </v-expansion-panels>


          <v-divider class="pb-4"></v-divider>

          <v-container class="pt-4 d-flex justify-end flex-column">
            <div class="pt-4">
                <v-btn color="primary"
                       data-cy="create-job-button"
                       :loading="loading"
                       @click="job_new"
                       large
                       v-if="!job_id">
                  Create
                </v-btn>
            </div>


            <v_error_multiple :error="job_new_error" data-cy="error-handler">
            </v_error_multiple>

            <v-row>
              <v-col cols="4">
                <v-btn color="primary"
                       data-cy="update-job-button"
                       :loading="loading"
                       @click="job_update"
                       v-if="job_id">
                  Update
                </v-btn>
              </v-col>
            </v-row>


          </v-container>
        </div>
        <div v-else>
          <v-select :items="instance_type_list"
                    v-model="job.instance_type"
                    label="Instance type"
                    data-cy="instance-type-select"
                    item-value="text"
                    :disabled="loading"
                    @change="">
          </v-select>

          <v-select :items="share_list"
                    v-model="job.share_object"
                    data-cy="share-select"
                    label="Share"
                    item-text="text"
                    return-object
                    :disabled="loading">
          </v-select>

          <v-select :items="type_list"
                    v-model="job.type"
                    data-cy="type-select"
                    label="Type"
                    item-value="text"
                    :disabled="loading">
          </v-select>

          <diffgram_select
            :item_list="file_handling_list"
            data-cy="file-handling-select"
            v-model="job.file_handling"
            label="File Handling"
            :disabled="loading"
          >
          </diffgram_select>

          <div v-if="$store.state.user.current.is_super_admin == true">
            <v-checkbox label="td_api_trainer_basic_training"
                        v-model="job.td_api_trainer_basic_training"
            >
            </v-checkbox>
          </div>

          <div v-if="['External', 'Shared'].includes(job.share)">
          </div>



          <v-expansion-panels>
            <v-expansion-panel>
              <div slot="header">Advanced</div>
              <v-expansion-panel-content>
                <v-select :items="review_by_human_frequency_list"
                          v-model="job.review_by_human_freqeuncy"
                          label="Review freqeuncy"
                          item-value="text"
                          :disabled="loading">
                </v-select>



                <!-- Disable changes for Jan 2019 release -->
                <v-select :items="permission_list"
                          v-model="job.permission"
                          label="Visibility"
                          item-value="text"
                          :disabled="true">
                </v-select>

              </v-expansion-panel-content>
            </v-expansion-panel>
          </v-expansion-panels>

          <div class="pt-4">

            <v-btn color="primary"
                   data-cy="create-job-button"
                   :loading="loading"
                   @click="job_new"
                   v-if="!job_id">
              Create
            </v-btn>
            <v-alert type="success"
                     :dismissible="true"
                     :value="success_action !== false">
              {{success_action}}
            </v-alert>

            <v_error_multiple :error="job_new_error" data-cy="error-handler">
            </v_error_multiple>


            <v-btn color="primary"
                   data-cy="update-job-button"
                   :loading="loading"
                   @click="job_update"
                   v-if="job_id">
              Update
            </v-btn>

          </div>
        </div>
      </v-col>
    </v-row>
    <label_manager_dialog @label_created="on_label_created" :project_string_id="project_string_id"
                          ref="label_manager_dialog"></label_manager_dialog>
  </v-container>

</template>

<script lang="ts">

  import axios from '../../../services/customAxiosInstance';
  import label_select_only from '../../label/label_select_only.vue'
  import label_manager_dialog from '../../label/label_manager_dialog.vue'
  import {route_errors} from '../../regular/regular_error_handling'
  import userscript_select from '../../annotation/userscript/userscript_select.vue'
  import Vue from "vue";


  export default Vue.extend({
      name: 'job_new_form',
      model: {
        prop: 'job',
        event: 'change'
      },
      components: {
        label_manager_dialog,
        label_select_only,
        userscript_select
      },
      props: {
        'job': {
          default: undefined,
          type: Object
        },
        'job_id': {
          default: undefined,
        },
        'project_string_id': {
          default: undefined,
          type: String
        },
        'quick_create': {
          default: false,
          type: Boolean
        }
      },

      data() {
        return {

          loading: false,
          error: {},
          success: false,
          mode: "cancel",
          instance_list: [],
          success_action: false,
          instance_type_list: ['polygon', 'box', 'text_tokens', 'tag'],
          type_list: ['Normal', 'Exam'],  // 'Learning' not supported yet right?
          share_list: [],
          file_handling_list: [
            {
              'display_name': 'Use Existing (Default)',
              'name': 'use_existing',
              'icon': 'mdi-cached',
              'color': 'primary'
            },
            {
              'display_name': 'Isolate (New Versions of Files)',
              'name': 'isolate',
              'icon': 'mdi-ab-testing',
              'color': 'primary'
            }
          ],
          job_new_error: {},
          review_by_human_frequency_list: ['every_3rd_pass', 'every_pass', 'every_10th_pass', 'No review'],
          label_mode_list: ['closed_all_available', 'closed_and_split_one_label_per_task', 'open'],
          field_list: ['Self Driving', 'Medical', 'Construction', 'Other'],
          passes_per_file_options: [1, 3],
          permission_list: ['Invite only', 'Only me', 'all_secure_users'],

        }
      },
      created() {
        let project_dict = {
          // TODO this may fail for org jobs? double check this.
          'text': this.$store.state.project.current.project_string_id + ' (Project)',
          'type': 'project'
        }
        this.share_list.splice(0, 0, project_dict)
        // caution we have this stuff here for type script
        // but share_list is a list so want to insert whole object here
        this.success_action = false;
        if (this.$store.state.org.current.id) {

          let org_dict = {
            'text': this.$store.state.org.current.name + ' (Organization)',
            'type': 'org'
          }
          // Insert at front so it's default option if it exists...
          this.share_list.splice(0, 0, org_dict)
        }
      },
      watch: {
        job_id: function () {

        },
        "job.interface_connection": function () {


          if (!this.job.interface_connection) {
            return
          }
          const connection = this.job.interface_connection;
          if(connection.integration_name == 'diffgram' ){
            this.instance_type_list = ['box', 'polygon', 'text_tokens', 'tag'];
            this.job.instance_type = this.instance_list[0];
            return;
          }
          if (!connection.supported_features) {
            return
          }

          const allowed_instance_types = connection.supported_features.allowed_instance_types;
          if (allowed_instance_types.length <= 0) {
            return
          }
          this.instance_type_list = allowed_instance_types;
          this.job.instance_type = this.instance_type_list[0];
          //this.$refs['instance_type'].change();           // this is a WIP maybe?

        }
      },
      methods: {
        on_label_created: function () {
          this.$refs.label_select.refresh_label_list_from_project();
        },
        open_labels_dialog: function () {
          this.$refs.label_manager_dialog.open()
        },
        receive_label_file: function (label_file_list) {
          // We need to get just the Id's no the entire object.
          this.job.label_file_list = label_file_list;
        },
        job_update: async function () {
          this.loading = true
          this.success_action = false
          const job = this.$props.job;
          job.share = job.share_object.type
          job.interface_connection_id = this.format_interface_id(job)
          this.job_new_error = {};
          try {
            const response = await axios.post(
              `/api/v1/project/${this.project_string_id}/job/update`,
              {
                ...job,
                job_id: job.id,
              }
            )
            // Handle job hash / draft / job status
            if (response.data.log.success == true) {

            }
            this.loading = false
            this.success_action = 'Job updated successfully.'
            this.$emit('job-updated', job)
            return response
          } catch (error) {
            this.loading = false
            this.job_new_error = route_errors(error)
            return false;
          }

        },

        job_new: async function () {
          this.loading = true
          this.success_action = false
          this.job_new_error = {}
          let job = {...this.$props.job};
          // QUESTION
          // Not clear if we want to do this as a computed property or...

          // careful to update with share property that's seperate due to dict thing.
          job.share = job.share_object.type
          job.interface_connection_id = this.format_interface_id(job)
          const url = `/api/v1/project/${this.project_string_id}/job/new`

          try {
            const response = await axios.post(url, job)
            // Handle job hash / draft / job status
            if (response.data.log.success == true) {
              this.$emit('job-created', response.data.job)
            }
            this.loading = false
            this.success_action = 'Job created successfully.'
            return response
          } catch (error) {
            console.error(error);
            this.loading = false
            this.job_new_error = route_errors(error)
            return error;
          }
        },

        format_interface_id (job) {
          let id = undefined
          if(!job){
            return id;
          }
          id = job.interface_connection ? job.interface_connection.id : undefined;
          return id
        }

      }
    }
  ) </script>

