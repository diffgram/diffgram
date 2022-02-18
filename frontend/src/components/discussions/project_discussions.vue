<template>

  <v-container fluid class="project-discussions-container">
    <main_menu>
    </main_menu>
    <div class="d-flex justify-end pr-8">
      <v-btn color="primary" @click="go_to_create_discussion"><v-icon>mdi-plus</v-icon>Create Discussion</v-btn>
    </div>
    <issues_table
      :project_string_id="project_string"
      @view_issue_detail="go_to_issue_detail"
    >

    </issues_table>


  </v-container>
</template>

<script lang="ts">

  import issues_table from '../discussions/issues_table';


  import Vue from "vue";
  import {create_event} from "../event/create_event"; export default Vue.extend( {
      name: 'project_discussions',
      props: {
        'project_string_id': undefined,
      },
      components: {
        issues_table
      },

      data () {
        return {

        }
      },
    mounted() {
        this.add_visit_history_event();
    },
    created() {
      },
      computed: {
        project_string: function(){
          let project_string_id = null;
          if (this.$route.query.project) {
            project_string_id = this.$route.query.project
          }
          else {
            // Fallback to current project if no query param is provided.
            project_string_id = this.$store.state.project.current.project_string_id;
          }
          return project_string_id
        }
      },
      methods: {
        add_visit_history_event: async function(){
          this.project_string_id = this.project_string;
          const event_data = await create_event(this.project_string_id, {
            page_name: 'project_discussion',
            object_type: 'page',
            user_visit: 'user_visit',
          })
        },
        go_to_issue_detail: function(discussion, task_template_id){
            this.$router.push(`/discussion/${discussion.id}/?project=${this.project_string}`);
        },
        go_to_create_discussion: function(){
          this.$router.push(`/discussions/create/?project=${this.project_string}`);
        }
      }
    }
  ) </script>

<style>
  .project-discussions-container{
    padding: 0 2rem;
    margin-top: 2rem;
  }
</style>
