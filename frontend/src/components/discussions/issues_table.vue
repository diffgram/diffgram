<template>
  <div>




        <v-row>
          <v-col cols="1" class="d-flex align-center">  <v-btn color="primary" @click="refresh_list" icon><v-icon>mdi-sync</v-icon></v-btn></v-col>
          <v-col cols="2">
            <diffgram_select
              v-if="allowed_filters.includes('type')"
              :item_list="type_list"
              v-model="type_filter"
              key_to_seperate_objects="value"
              label="Type"
              height="20"
              class="d-flex align-center mt-2"
              style="font-size: 12px; min-height: 30px !important; justify-self: flex-end;"
              item-text="text"
              item-value="value">
            </diffgram_select>
          </v-col>
          <v-col cols="2">
            <diffgram_select
                      v-if="allowed_filters.includes('status')"
                      :item_list="status_list"
                      v-model="status_filter"
                      key_to_seperate_objects="value"
                      label="Status"
                      height="20"
                      class="d-flex align-center mt-2"
                      style="font-size: 12px; min-height: 30px !important; justify-self: flex-end;"
                      item-text="text"
                      item-value="value">
            </diffgram_select>
          </v-col>
          <v-col cols="2" class="d-flex align-center"  v-if="allowed_filters.includes('job')">
            <job_select
              v-model="job"
              label="Job"
            >
            </job_select>
          </v-col>
          <v-col cols="3">
            <date_picker
              v-if="allowed_filters.includes('date')"
              @date="date = $event"
              :with_spacer="false"
              :initialize_empty="true"
            >
            </date_picker>
          </v-col>

        </v-row>

      <regular_table
        v-if="!loading && issues_list"
        :item_list="filtered_issues_list"
        :column_list="columns_issues"
        :elevation="0"
        :items_per_page="5"
        v-model="selected_cols"
        :header_list="headers_issues">

        <template slot="title" slot-scope="props">
          <div class="d-flex align-center">
            <v-icon color="primary" class="mr-4" v-if="props.item.type === 'discussion' && props.item.status === 'open'">mdi-comment-text-multiple</v-icon>
            <v-icon color="primary" class="mr-4" v-if="props.item.type === 'discussion' && props.item.status === 'closed'">mdi-comment-off</v-icon>
            <v-icon color="success" class="mr-4" v-if="props.item.type === 'issue' && props.item.status === 'closed'">mdi-lock-check</v-icon>
            <v-icon color="warning" class="mr-4"  v-if="props.item.type === 'issue' && props.item.status === 'open'" >mdi-alert</v-icon>
            <div class="d-flex flex-column justify-end pt-4" style="height: 100%">
              <a class="font-weight-bold" @click="view_issue_detail(props.item)"> {{props.item.title}} </a>
              <p style="font-size: 9px; font-weight: bold; color: #323232">
                Opened: {{props.item.created_time| moment("ddd, MMMM Do YYYY")}} {{props.item.user ? `By:
                ${props.item.user.first_name} ${props.item.user.last_name}` : ''}}
              </p>
            </div>
          </div>
        </template>
      </regular_table>


    <v-skeleton-loader type="table-row@3" v-if="loading">

    </v-skeleton-loader>

  </div>
</template>

<script lang="ts">

  import axios from '../../services/customInstance';
  import attribute_home from '../attribute/attribute_home'


  import Vue from "vue";

  export default Vue.extend({
      name: 'issues_table',

      components: {
        attribute_home
      },

      /*
       * TODO
       * Switch to each "sub part" simply declares if it's rendered or now,
       * NOT having to know about a
       * "mode" since then it has to know about the context in which it's being used!!!
       * ie "render_attributes" : { default: true}
       */

      props: {
        'project_string_id': undefined,
        'allowed_filters': {
          type: Array,
          default: () => ['job', 'date', 'status', 'type']
        },
        'file': undefined,
        'current_issue': undefined,
        'task_template_id': undefined,
        'task': undefined
      },
      watch: {
        task: function (newval, oldval) {
          if (newval && newval.id && newval.id != oldval.id) {
            this.get_issues_list()
          }
        },
        task_template_id: function (newval, oldval) {
          if (newval && newval.id && newval.id != oldval.id) {
            this.get_issues_list()
          }
        },
        file: function (newval, oldval) {
          if (newval && newval != oldval) {
            this.get_issues_list()
          }
        }
      },
      beforeMount() {

      },
      mounted() {
        this.get_issues_list();
      },

      data() {
        return {
          loading: false,
          issues_list: [],
          date: undefined,
          job: undefined,
          status_filter: 'open',
          type_filter: 'all',
          status_list: [
            {
              name: 'Closed',
              value: 'closed'
            },
            {
              name: 'Opened',
              value: 'open'
            },
          ],
          type_list: [
            {
              name: 'All',
              value: 'all'
            },
            {
              name: 'Issues',
              value: 'issue'
            },
            {
              name: 'Discussions',
              value: 'discussion'
            },
          ],
          headers_issues: [
            {
              text: "Issue",
              align: 'left',
              sortable: true,
              value: 'title'
            },
          ],
          columns_issues: ['title'],
          selected_cols: [],
        }
      },
      computed: {
        filtered_issues_list: function () {
          return this.issues_list;
        }

      },
      methods: {
        view_issue_detail(new_issue) {
          this.$emit('view_issue_detail', new_issue, this.$props.task_template_id ? this.$props.task_template_id : undefined)
        },
        add_issue_to_list(new_issue) {
          this.issues_list.push(new_issue)
        },
        refresh_list(){
          this.get_issues_list();
        },
        async get_issues_list() {
          if (!this.$props.task && !this.$props.task_template_id && this.$props.file_id) {
            return;
          }
          this.loading = true;
          try {
            let task_template_id = undefined;
            if(!this.job){
              task_template_id = parseInt(this.$props.task_template_id);
            }
            else{
              task_template_id = parseInt(this.job.id, 10);
            }
            let  type_filter_value = this.type_filter;
            if(this.type_filter === 'all'){
              type_filter_value = undefined

            }
            const response = await axios.post(`/api/v1/project/${this.$props.project_string_id}/discussions/list`,
              {
                'task_id': this.$props.task ? this.$props.task.id : undefined,
                'job_id': task_template_id,
                'starts': this.date ? this.date.from : undefined,
                'ends': this.date ? this.date.to : undefined,
                'status': this.status_filter ? this.status_filter : undefined,
                'type': type_filter_value ? type_filter_value: undefined,
                'file_id': this.$props.file_id
              }
            )
            if (response.data && response.data.issues) {
              this.issues_list = response.data.issues;
            }
          } catch (error) {
            console.error(error)
          } finally {
            this.loading = false;
          }
        }
      }
    }
  ) </script>
