<template>
  <v-layout>
    <v-row>
      <v-col cols="12" class="pa-0 d-flex align-center">

        <!--
            @input is built right into vue js
           https://vuejs.org/v2/guide/components.html#Using-v-model-on-Components
          -->

        <!--

          Concrete implementation of getting job list for selection

          TODO would like to use diffgram selector (ie so we could include
          counts or something) but it would require changing
          job list around a bit
        -->

        <v-autocomplete
          :items="job_list"
          v-model="job_internal"
          :label="label"

          return-object
          item-text="name"
          @input="$emit('input', $event)"
          @change="$emit('change', $event)"
          :loading="loading || loading_internal"
          :disabled="disabled || loading_internal"
          @focus="job_list_api()"
          clearable
        >

          <template v-slot:item="data">

            <span>
              {{data.item.name}}
             </span>

          </template>

          <template v-slot:selection="data">

            <span>
              {{data.item.name}}
             </span>

          </template>


        </v-autocomplete>
        <button_with_menu
          tooltip_message="New Job"
          icon="add"
          :close_by_button="false"
          v-if="!view_only_mode"
          offset="x"
          menu_direction="left"
          color="primary"
          :commit_menu_status="true"
          font_size="small"
          ref="add_job_menu"
        >
          <template slot="content">
            <v-layout style="max-width: 250px">
              <job_new_form
                :quick_create="true"
                :job="job_empty_template"
                :project_string_id="project_string_id"
                ref="job_create_form"
                @job-created="on_job_created"
              >
              </job_new_form>
            </v-layout>
          </template>

        </button_with_menu>
        <button_with_menu
          tooltip_message="Edit Job"
          icon="edit"

          :close_by_button="true"
          v-if="!view_only_mode && job_internal && Object.keys(job_internal).length !== 0 && job_internal.constructor === Object"
          menu_direction="left"
          offset="x"
          color="black"
          :loading="loading_job_fetch"
          :commit_menu_status="true"
          font_size="small"
          ref="edit_job_menu"
          @click="fetch_job"
        >

          <template slot="content">
            <v-layout style="max-width: 250px">
              <job_new_form
                :quick_create="true"
                v-if="!loading_job_fetch && job_edit"
                :job="job_edit"
                :job_id="job_edit.id"
                :project_string_id="project_string_id"
                @job-updated="on_job_updated"
              >
              </job_new_form>
              <v-skeleton-loader :loading="true" height="200px" width="200px" type="article, actions"
                                 v-else
                                 class="full-width skeleton-loader-autocomplete">
              </v-skeleton-loader>
            </v-layout>

          </template>

        </button_with_menu>
      </v-col>
    </v-row>
  </v-layout>


</template>

<script lang="ts">

  /*

  EXAMPLE WIP

  <job_select
      :item_list="status_filters_list"
      v-model="job"
      label="Job"
      :disabled="loading"
      >
  </job_select>

   */

  import Vue from "vue";
  import axios from 'axios';
  import sillyname from 'sillyname';
  import job_new_form from './job_new_form';

  export default Vue.extend({

      // 'select' is a reserved name
      name: 'job_select',
      props: {
        // built in vue js
        'value': {
          default: null,
          type: Object
        },
        'view_only_mode': {
          default: true,
          type: Boolean
        },
        'label': {
          default: "Job",
          type: String
        },
        'loading': {
          default: false,
          type: Boolean
        },
        'disabled': {
          default: false,
          type: Boolean
        },
        'select_this_id': {
          default: null
        },
        'loading_job': {
          default: false
        },
        'status': {
          default: undefined
        }
      },
      components: {
        job_new_form: job_new_form
      },
      data() {
        return {
          job_internal: null,
          loading_internal: false,
          job_list: [],
          job_empty_template: {
            name: sillyname().split(" ")[0],
            label_mode: 'closed_all_available',
            passes_per_file: 1,
            share_object: {
              // TODO this may fail for org jobs? double check this.
              'text': String,
              'type': 'project'
            },
            share: 'project',
            instance_type: 'box', //"box" or "polygon" or... "text"...
            permission: 'all_secure_users',
            field: 'Other',
            category: 'visual',
            type: 'Normal',
            connector_data: {},
            //  default to no review while improving review system
            review_by_human_freqeuncy: 'No review', //'every_3rd_pass'
            td_api_trainer_basic_training: false,
            file_handling: "use_existing",
            project_string_id: ''
          },
          loading_job_fetch: false,
          job_edit: undefined,
        }
      },
      created() {
        this.job_internal = this.value
        this.project_string_id = this.$store.state.project.current.project_string_id;
        this.job_empty_template.share_object = {
          type: 'project',
          text: this.$store.state.project.current.project_string_id + ' (Project)'
        };
        // Just default to loading this for now
        this.job_list_api()

      },
      watch: {
        select_this_id: function () {
          // watch because the id may not be available
          // when component first loads or may change

          this.update_job_from_external_id()
        }
      },
      methods: {
        on_job_updated: function (job) {
          this.job_list = this.job_list.map(elm => {
            if (elm.id === job.id) {
              return job
            }
            return elm;
          });
          this.job_internal = job;
        },
        on_job_created: function (job) {
          this.job_list.push(job);
          this.job_empty_template = {
            name: sillyname().split(" ")[0],
            label_mode: 'closed_all_available',
            passes_per_file: 1,
            share_object: {
              // TODO this may fail for org jobs? double check this.
              'text': String,
              'type': 'project'
            },
            share: 'project',
            instance_type: 'box', //"box" or "polygon" or... "text"...
            permission: 'all_secure_users',
            field: 'Other',
            category: 'visual',
            type: 'Normal',
            connector_data: {},
            //  default to no review while improving review system
            review_by_human_freqeuncy: 'No review', //'every_3rd_pass'
            td_api_trainer_basic_training: false,
            file_handling: "use_existing",
            project_string_id: ''
          };
          this.job_empty_template.share_object = {
            type: 'project',
            text: this.$store.state.project.current.project_string_id + ' (Project)'
          };
          this.job_internal = job;
          this.$emit('change', job)
          this.$emit('input', job)
          this.$refs.add_job_menu.close_menu();
        },
        update_job_from_external_id: function () {
          /*  Careful the job list may not be available
           *  on first load, so we may need to call this
           *  after job list has been selected...
           */

          if (!this.select_this_id) {
            return
          }

          let job = this.job_list.find(
            x => {
              return x.id == parseInt(this.select_this_id)
            })

          if (job) {
            this.job_internal = job
            this.$emit('change', this.job_internal)
          }

          //console.log(this.job_internal)
        },
        fetch_job: function () {
          // Just fetch if we have a job selected.
          if (!this.job_internal || !this.job_internal.id) {
            return;
          }
          this.loading_job_fetch = true;
          axios.post(`/api/v1/job/${this.job_internal.id}/builder/info`, {
            'mode_data': 'job_edit',
          }).then(response => {

            this.job_edit = {
              ...this.job_edit,
              ...response.data['job']
            }
            this.job_edit.share_object = {
              type: 'project',
              text: this.$store.state.project.current.project_string_id + ' (Project)'
            };

            this.loading_job_fetch = false

          })
            .catch(error => {
              console.log(error);
              this.loading_job_fetch = false;
            });
        },
        job_list_api() {

          // Return if we already have job list
          // since at the moment we call this on every @focus event
          if (this.job_list.length != 0) {
            return
          }

          // do we want to reset {job} when we run this?
          this.loading_internal = true

          // TODO not sure if these search parameters make sense here
          // ie is this only doing completed jobs or...

          /*
           *  At the moment this assumes in the scope of a project...
           *
           */
          let status = 'All';
          if (this.$props.status) {
            status = this.$props.status;
          }

          axios.post('/api/v1/job/list', {

            metadata: {
              'my_jobs_only': false,
              'builder_or_trainer': this.$store.state.builder_or_trainer,
              'data_mode': 'name_and_id_only',
              'project_string_id': this.$store.state.project.current.project_string_id,
              'status': status
            }

          }).then(response => {

            if (response.data['Job_list'] != null) {

              this.job_list = response.data['Job_list']
              this.loading_internal = false
              // Set default item

              if (this.select_this_id) {
                this.update_job_from_external_id()
              } else {
                if (this.job_list && this.job_list.length > 0) {
                  this.job = this.job_list[0]
                }
              }


            }

          })
            .catch(error => {
              console.log(error);
              this.loading_internal = false
            });
        }

      }
    }
  ) </script>
