<template>
  <v-list
    subheader
    two-line
    v-if="!loading"
    class="pa-0 ma-0"
  >
    <v-list-item
      v-for="history in user_visit_history"
      :key="history.id"
      dense
      class="pa-0 ma-0"

    >
      <v-list-item-avatar size="28"
                          @click="go_to_history(history, false)"
                          style="cursor: pointer;"
                          >
        <v-icon
          class="grey lighten-1"
          dark
          color="primary"
          size="16"
          v-if="history.file_id"
        >
          mdi-folder
        </v-icon>
        <v-icon
          size="16"
          class="primary lighten-2"
          dark
          v-else-if="history.task_id"
        >
          mdi-checkbox-multiple-marked
        </v-icon>
        <v-icon
          size="16"
          class="primary lighten-2"
          dark
          v-else
        >
          mdi-page-next-outline
        </v-icon>
      </v-list-item-avatar>

      <v-list-item-content  @click="go_to_history(history, false)"
                            style="cursor: pointer;">

        <v-list-item-title v-if="history.file_id" v-text="`File: ${history.file_id}`"></v-list-item-title>
        <v-list-item-title v-else-if="history.task_id" v-text="`Task: ${history.task_id}`"></v-list-item-title>
        <v-list-item-title v-else-if="history.job_id" v-text="`Task Template: ${history.job_id}`"></v-list-item-title>
        <v-list-item-title v-else v-text="determine_link_from_page_name(history).name"></v-list-item-title>

        <v-list-item-subtitle v-if="history.time_created" v-text="history.time_created"></v-list-item-subtitle>
      </v-list-item-content>

      <v-list-item-action>
        <v-btn icon @click="go_to_history(history, true)">
          <v-icon color="primary lighten-1">mdi-open-in-new</v-icon>
        </v-btn>
      </v-list-item-action>
    </v-list-item>
  </v-list>
  <v-progress-circular class="ma-auto d-flex justify-center align-center" size="46" indeterminate v-else color="primary"></v-progress-circular>
</template>

<script>
import axios from '../../services/customInstance';
import Vue from "vue";

export default Vue.extend( {
  name: 'user_visit_history_list',
  props: ['project_string_id'],
  mounted() {
    this.fetch_user_visit_history();
  },
  data() {
    return {
      project: {
        images_count: 0
      },
      loading: false,
      checks: {},
      user_visit_history: undefined,
    }
  },
  methods: {
    go_to_history: function(history, new_tab){
      let routeData = this.determine_link_from_page_name(history).link
      if(history.task_id){
        routeData = `/task/${history.task_id}`;
      }
      else if(history.file_id){
        routeData = `/file/${history.file_id}`;
      }
      else if(history.job_id){
        routeData = `/job/${history.job_id}`;
      }

      if(new_tab){
        window.open(routeData, '_blank');
      }
      else{
        this.$router.push(routeData)
      }

    },
    determine_link_from_page_name: function(history){
      if(history.page_name === 'label_templates'){
        return {
          name: 'Schema - Labels, Attributes, Templates',
          link: `/project/${history.project_string_id}/labels`,
        };
      }
      else if(history.page_name === 'connection_list'){
        return {
          name: 'Connections Dashboard',
          link: `/connections/list`,
        };
      }
      else if(history.page_name === 'data_explorer'){
        return {
          name: 'Studio - Data Explorer',
          link: `/studio/annotate/${history.project_string_id}`,
        }
      }
      else if(history.page_name === 'project_discussion'){
        return {
          name: 'Discussions Dashboard',
          link: `/discussions/?project=${history.project_string_id}`,
        };
      }
      else if(history.page_name === 'event_list'){
        return {
          name: 'Event Dashboard',
          link: `/project/${history.project_string_id}/events`,
        };
      }
      else if(history.page_name === 'export_dashboard'){
        return {
          name: 'Exports',
          link: `/project/${history.project_string_id}/export`,
        };
      }
      else if(history.page_name === 'project_manager'){
        return {
          name: 'Projects',
          link: `/projects`,
        };
      }
      else if(history.page_name === 'project_settings'){
        return {
          link: `/project/${history.project_string_id}/settings`,
          name:  'Project Settings'
        };
      }
      else if(history.page_name === 'reports_dashboard'){
        return {
          link: `/report/list/?project=${history.project_string_id}`,
          name:  'Reports'
        };
      }
      else if(history.page_name === 'sync_events_list') {
        return {
          link: `/sync-events/list?project_id=${history.project_string_id}`,
          name: 'Stream Events List'
        };
      }
      else if(history.page_name === 'credential_list'){
        return {
          link: `/credential/list`,
          name: 'Awards List'
        };
      }
      else if(history.page_name === 'job_list'){
        return {
          link: `/job/list`,
          name: 'Tasks'
        };
      }
      else if(history.page_name === 'guide_list'){
        return {
          link: `/project/${history.project_string_id}/guide/list`,
          name: 'Guides List'
        };
      }
      else if(history.page_name === 'import_dashboard'){
        return {
          link: `/studio/upload/${history.project_string_id}`,
          name:  'Imports'
        };
      }
      else{
        return{
          name: '',
          link: ''
        }
      }



    },
    remove_duplicate_element: function(user_visit_history_list){
      let index_to_exclude = [];
      for(let i = 0; i < user_visit_history_list.length; i++){
        let current = user_visit_history_list[i];
        let j = i + 1;
        if(index_to_exclude.includes(i)){
          continue
        }
        if(j === user_visit_history_list.length - 1){
          continue
        }
        let next = user_visit_history_list[j];
        if(!next){
          continue
        }
        if(current.page_name !== 'file_detail' || current.page_name !== 'task_detail'){
          while(current.page_name === next.page_name){
            index_to_exclude.push(j)
            j += 1;
            if(j === user_visit_history_list.length - 1){
              break
            }
            next = user_visit_history_list[j];
          }
        }
        else if(current.page_name === 'file_detail'){
          while(current.file_id === next.file_id){
            index_to_exclude.push(j)
            j += 1;
            if(j === user_visit_history_list.length - 1){
              break
            }
            next = user_visit_history_list[j];
          }
        }
        else if(current.page_name === 'task_detail'){
          while(current.task_id === next.task_id){
            index_to_exclude.push(j)
            j += 1;
            if(j === user_visit_history_list.length - 1){
              break
            }
            next = user_visit_history_list[j];
          }
        }

      }
      return user_visit_history_list.filter((elm, i) => { return !index_to_exclude.includes(i)})
    },
    fetch_user_visit_history: async function(){
      try{
        this.loading = true
        const response = await axios.post(`/api/v1/${this.$props.project_string_id}/user-visit-history/`, {
          limit: 15
        });
        if(response.status === 200){
          this.user_visit_history = response.data.user_visit_events;
          this.user_visit_history = this.remove_duplicate_element(this.user_visit_history);
          this.$store.commit('set_user_state', ['history', this.user_visit_history])
        }
      }
      catch (e) {
        console.error(e);
      }
      finally {
        this.loading = false;
      }
    }
  },
  watch: {
    '$route': 'get_project'
  }
})

</script>

<style scoped>

</style>
