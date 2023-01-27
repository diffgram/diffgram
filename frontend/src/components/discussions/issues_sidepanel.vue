<template>
  <div v-cloak>

    <v-container fluid style="border: 1px solid #ababab"
                 v-if="!loading && issues_ui_manager.issues_list.length == 0"
                 class="d-flex flex-column align-center justify-center ma-0">
      <h1>No Issues.</h1>
      <v-icon size="250" color="green">mdi-check</v-icon>
    </v-container>

    <v-expand-transition>
      <v-card-text class="pa-0" >

        <v-container  v-if="!loading && issues_ui_manager.issues_list.length > 0" class="d-flex flex-column pa-1">

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

  import axios from '../../services/customInstance';
  import attribute_home from '../attribute/attribute_home'


  import Vue from "vue";
  import IssuesAnnotationUIManager from "../annotation/issues/IssuesAnnotationUIManager";
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
        'task': undefined,
        'issues_ui_manager': {type: Object as IssuesAnnotationUIManager, required: true}
      },
      watch: {
        task: function(newval, oldval){
          this.get_if_new_value(newval, oldval)
        },
        file: function(newval, oldval){
          this.get_if_new_value(newval, oldval)
        }
      },
      beforeMount() {

      },
      mounted() {
        this.get_issues_list()
      },

      data() {
        return {
          loading: false,
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
          return this.issues_ui_manager.issues_list.filter(elm => elm.status === this.status_filter);
        }

      },
      methods: {

        get_if_new_value(newval, oldval){
          if(newval == null) {return}
          if(newval.id && oldval == null) {
            this.get_issues_list()
          }
          else if(newval.id && newval.id != oldval.id){
            this.get_issues_list()
          }
        },
        minimize_panel(){
          this.$emit('minimize_issues_panel', true)
        },
        maximize_panel(){
          this.$emit('maximize_issues_panel', true)
        },
        view_issue_detail(new_issue){
          this.$emit('view_issue_detail', new_issue)
        },
        async get_issues_list() {

          if(!this.$props.task && !this.$props.file){
            return;
          }
          let task_id, file_id;
          if(this.$props.task){
            task_id = this.$props.task.id
          }
          if(this.$props.file){
            file_id = this.$props.file.id
          }
          this.loading = true;
          try {
            const issues_list = await this.issues_ui_manager.get_issues_list(this.$props.project_string_id, task_id, file_id)
            if (issues_list) {
              this.$emit('issues_fetched', issues_list);
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
