<template>
  <div v-cloak v-if="issues_list.length > 0">



        <v-card-title class="d-flex justify-start align-center">

          <v-icon left color="primary" size="28">mdi-comment-multiple</v-icon>
          Discussions

          <v-spacer></v-spacer>

          <v-btn @click="maximize_panel" v-if="minimized" icon>
            <v-icon>mdi-chevron-down</v-icon>
          </v-btn>
          <v-btn @click="minimize_panel" v-if="!minimized" icon>
            <v-icon>mdi-chevron-up</v-icon>
          </v-btn>
        </v-card-title>
        <v-expand-transition>
          <v-card-text v-show="!minimized" class="pa-0" >
            <v-container  v-if="!loading && issues_list" class="d-flex flex-column pa-1">
              <v-select :items="status_list"
                        v-model="status_filter"
                        label="Status"
                        height="20"
                        class="align-self-end pa-0"
                        style="width: 30%; font-size: 12px; min-height: 30px !important; justify-self: flex-end; margin-bottom: auto"
                        item-text="text"
                        item-value="value">
              </v-select>
              <!--
                Please note that this code is almost same as issues_table.vue. Decided to leave it duplicate since I have
                the feeling that both table might grow in different directions in the future since one is on the studio
                and the other is in the context of the job_detail or project context.
              -->
                <regular_table
                  style="max-height: 350px; overflow-y: auto"
                  :item_list="filtered_issues_list"
                  :column_list="columns_issues"
                  :items_per_page="5"
                  v-model="selected_cols"
                  :header_list="headers_issues">

                  <template slot="title" slot-scope="props">
                    <div class="d-flex align-center">
                      <v-icon color="success" class="mr-4" v-if="props.item.status === 'closed'">mdi-lock-check</v-icon>
                      <v-icon color="warning" class="mr-4" v-else>mdi-alert</v-icon>
                      <div class="d-flex flex-column justify-end pt-4" style="height: 100%">
                        <a class="font-weight-bold" @click="view_issue_detail(props.item)"> {{props.item.title}} </a>
                        <p style="font-size: 9px; font-weight: bold; color: #323232">
                          Opened: {{props.item.created_time| moment("ddd, MMMM Do YYYY")}} {{props.item.user ? `By: ${props.item.user.first_name} ${props.item.user.last_name}` : ''}}
                        </p>
                      </div>
                    </div>
                  </template>

                </regular_table>

            </v-container>
          </v-card-text>
        </v-expand-transition>

        <!-- And minimized false because otherwise when saving it
          "pushes" it down and is visually distracting. question if it's better
          to have this in expand-transition then all game for that. -->
        <v-skeleton-loader :loading="loading" type="table-row@3"
              v-if="loading && minimized == false">

        </v-skeleton-loader>

  </div>
</template>

<script lang="ts">

  import axios from 'axios';
  import attribute_home from '../attribute/attribute_home'


  import Vue from "vue";
  import moment from "vue-moment";
  export default Vue.extend({
      name: 'issues_sidepanel',

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
        'project_string_id': {},
        'file': undefined,
        'minimized': {
          default: false,
          type: Boolean
        },
        'current_issue': undefined,
        'task': undefined
      },
      watch: {
        task: function(newval, oldval){
          if(newval.id && newval.id != oldval.id){
            this.get_issues_list()
          }
        },
        file: function(newval, oldval){
          if(newval && newval.id != oldval.id){
            this.get_issues_list()
          }
        }
      },
      beforeMount() {

      },
      mounted() {

      },

      data() {
        return {
          loading: false,
          issues_list: [],
          status_filter: 'open',
          status_list: [
            {
              text: 'Closed',
              value: 'closed'
            },
            {
              text: 'Opened',
              value: 'open'
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
        filtered_issues_list: function(){
          return this.issues_list.filter(elm => elm.status === this.status_filter);
        }

      },
      methods: {
        minimize_panel(){
          this.$emit('minimize_issues_panel', true)
        },
        maximize_panel(){
          this.$emit('maximize_issues_panel', true)
        },
        update_issue(updated_issue){
          this.issues_list = this.issues_list.map(issue =>{
            if(issue.id === updated_issue.id){
              return {
                ...updated_issue
              }
            }
            return issue
          })
        },
        view_issue_detail(new_issue){
          this.$emit('view_issue_detail', new_issue)
        },
        add_issue_to_list(new_issue){
          this.issues_list.push(new_issue)
        },
        async get_issues_list() {
          if(!this.$props.task && !this.$props.file){
            return;
          }
          this.loading = true;
          try {
            const response = await axios.post(`/api/v1/project/${this.$props.project_string_id}/discussions/list`,
              {
                'task_id': this.$props.task ? this.$props.task.id : undefined,
                'file_id': this.$props.file ? this.$props.file.id : undefined,
              }
            )
            if (response.data && response.data.issues) {
              this.issues_list = response.data.issues;
              this.$emit('issues_fetched', this.issues_list);
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
