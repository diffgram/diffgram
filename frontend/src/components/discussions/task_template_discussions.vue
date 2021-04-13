<template>

  <v-container class="pa-2" fluid fill-height>
    <v-layout child-flex>
      <v-card class="pa-0" flat width="100%">
        <v_error_multiple :error="list_discussions_error">
        </v_error_multiple>
        <v-card-title class="d-flex justify-start align-center">
          <h2>
            <v-icon left size="36">mdi-comment-multiple</v-icon>
            <span>Discussions</span>
          </h2>
        </v-card-title>

        <issues_table
          :project_string_id="project_string_id"
          :allowed_filters="['status', 'date']"
          :task_template_id="task_template_id"
          @view_issue_detail="go_to_issue_detail"
        ></issues_table>

      </v-card>
    </v-layout>
  </v-container>

</template>

<script lang="ts">

  import axios from 'axios';


  import Vue from "vue";
  import issues_table from "../discussions/issues_table";

  export default Vue.extend({
      name: 'task_template_discussions',
      components: {
        issues_table,
      },
      props: {
        'project_string_id': undefined,
        'task_template_id': undefined,
      },
      watch: {},
      beforeMount() {

      },
      mounted() {

      },

      data() {
        return {
          loading: false,
          discussions_list: [],
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
          list_discussions_error: {}
        }
      },
      computed: {},
      methods: {
        go_to_issue_detail: function(discussion, task_template_id){
          if(task_template_id){
            this.$router.push(`/job/${task_template_id}/discussion/${discussion.id}?project=${this.$props.project_string_id}`);
          }
          else{
            this.$router.push(`/discussion/${discussion.id}?project=${this.$props.project_string_id}`);

          }

        }
      }
    }
  ) </script>
