<template>
  <div id="annotator_dashboard" class="home-container">


  <v-container>
    <v-card>
      <v-container>
        <h1>Annotate Next Available Task </h1>
          <div class="pa-2">
            <v-btn
              color="primary"
              x-large
              data-cy="annotate_now"
              @click="api_get_next_task_annotator()"
            >
              Annotate Now
            </v-btn>
          </div>
      </v-container>
    </v-card>
  </v-container>

    <v-container>
      <v-card>
        <v-container>
          <h2>Resume Last Task </h2>
            <div class="pa-2">
              <v-btn
                color="primary"
                large
                data-cy="resume_last_task"
                :disabled="last_task === false"
                @click="route_last_task()"
              >
                Resume
              </v-btn>
              <div v-if="last_task" class="pt-2 font-weight-light">
                {{last_task.time_created}}
                {{last_task.project_string_id}}
                {{last_task.task_id}}
              </div>
            </div>
          </v-container>
      </v-card>
    </v-container>

    <v-container>
      <v-card>
        <v-container>
          <h2>Browse & Search Tasks </h2>
            <div class="pa-2">
              <v-btn
                color="primary"
                large
                data-cy="serach_route"
                @click="$router.push('/job/list')"
              >
                Browse Now
              </v-btn>
            </div>
          </v-container>
      </v-card>
    </v-container>

    <v-container>
      <v-card>
        <v-container>
          <h2>My Visit History</h2>
             <user_visit_history_list :project_string_id="project_string_id"></user_visit_history_list>
          </v-container>
      </v-card>
    </v-container>

  </div>
</template>

<script lang="ts">

import axios from 'axios';
import report_dashboard from '../../report/report_dashboard'
import user_visit_history_list from '../../event/user_visit_history_list.vue'
import project_pipeline from '../../project/project_pipeline'

import Vue from "vue";

export default Vue.extend( {
  name: 'annotator_dashboard',
  components: {
    report_dashboard,
    user_visit_history_list,
    project_pipeline,

  },
  data () {
    return {


    }
  },
  created() {

  },
  mounted() {

  },
  computed: {
    project_string_id: function(){
      return this.$store.state.project.current.project_string_id;
    },
    last_task: function (){
      if (!this.$store.state.user.history) { return false }
      const last_task = this.$store.state.user.history.find(
        x => x.page_name == 'task_detail')

      return last_task
    }
  },
  methods: {
    route_last_task: function(){
      const routeData = `/task/${this.last_task.task_id}`;
      this.$router.push(routeData)
    },

    api_get_next_task_annotator: async function(){
      try{
        this.loading = true
        const response = await axios.post(
          `/api/v1/project/${this.project_string_id}/task/next`, {
        });
        if(response.status === 200){
          let task = response.data.task
          const routeData = `/task/${task.id}`;
          this.$router.push(routeData)
        }
      }
      catch (e) {
        console.error(e);
      }
      finally {
        this.loading = false;
      }
    }

  }
}
) </script>

<style scoped>
  .home-container{
    padding: 0 10rem;
  }
</style>

