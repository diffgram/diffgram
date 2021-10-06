<template>
  <div id="annotator_dashboard" class="home-container">


  <v-container>
    <v-card>
      <v-container>

      <v-progress-linear
        v-if="next_task_loading"
        height="10"
        indeterminate
        absolute
        top
        color="secondary accent-4">
      </v-progress-linear>

        <h1>Annotate Next Available Task </h1>
          <div class="pa-2">
            <v-btn
              color="primary"
              x-large
              data-cy="annotate_now"
              :disabled="next_task_loading"
              @click="api_get_next_task_annotator()"
            >
              Annotate

                  <v-icon
                    right
                  >
                    mdi-play
                  </v-icon>

            </v-btn>
          </div>
      </v-container>
    </v-card>
  </v-container>

    <v-container>
      <v-card>
        <v-container>

        <v-progress-linear
          v-if="resume_task_loading"
          height="10"
          indeterminate
          absolute
          top
          color="secondary accent-4">
        </v-progress-linear>

          <h2>Resume Last Task </h2>
            <div class="pa-2">
              <v-btn
                color="primary"
                large
                data-cy="resume_last_task"
                :disabled="last_task === false || resume_task_loading"
                @click="route_resume_task()"
              >
                Resume

                  <v-icon
                    right
                  >
                    mdi-replay
                  </v-icon>

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
                Browse

                  <v-icon
                    right
                  >
                    mdi-compass
                  </v-icon>

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
      next_task_loading : false,
      resume_task_loading: false
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

    route_resume_task: function(){
      this.resume_task_loading = true
      const routeData = `/task/${this.last_task.task_id}`;
      this.$router.push(routeData)
    },

    api_get_next_task_annotator: async function(){
      try{
        this.next_task_loading = true
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
        this.next_task_loading = false;
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

