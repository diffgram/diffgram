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

              <v-layout>
                <div class="d-flex align-center justify-center">
                  <v-btn
                    color="primary"
                    large
                    data-cy="resume_last_task"
                    :disabled="!last_task_event || resume_task_loading || (last_task_event && !last_task_event.task_id)"
                    @click="route_resume_task()"
                  >
                    Resume

                      <v-icon
                        right
                      >
                        mdi-replay
                      </v-icon>

                  </v-btn>
                </div>


                <div class="pl-4"
                     v-if="last_task_event
                        && last_file">

                    <file_preview_with_hover_expansion
                      :file="last_file"
                      v-if="project_string_id == last_task_event.project_string_id"
                      :project_string_id="last_task_event.project_string_id"
                      tooltip_direction="right"
                      @view_file_detail="route_resume_task()"
                                                       >
                    </file_preview_with_hover_expansion>

                  <!--
                    <file_preview
                      v-if="project_string_id == last_task_event.project_string_id"
                      class="d-flex file-preview"
                      file_preview_width="150"
                      file_preview_height="150"
                      :key="last_task_event.task.id"
                      :project_string_id="last_task_event.project_string_id"
                      :file="last_file"
                      :instance_list="last_file.instance_list"
                      :show_ground_truth="true"
                      @view_file_detail="route_resume_task()"
                    ></file_preview>
                  -->

                    <div @click="route_resume_task()"
                         v-if="project_string_id != last_task_event.project_string_id"
                         >
                      <thumbnail
                        v-if="last_file.type === 'video'
                           || last_file.type === 'image'"
                        :item="last_file"
                      >
                      </thumbnail>
                    </div>


                </div>

                <div v-if="last_task_event"
                     class="pa-2 font-weight-light flex-column d-flex">
                  <div>
                  {{last_task_event.time_created}}
                  </div>
                  <div>
                  {{last_task_event.project_string_id}}
                  </div>
                  <div>
                  {{last_task_event.task_id}}
                  </div>
                </div>


             </v-layout>
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

<!--    <v-container>-->
<!--      <v-card>-->
<!--        <v-container>-->
<!--          <h2>My Visit History</h2>-->
<!--             <user_visit_history_list :project_string_id="project_string_id"></user_visit_history_list>-->
<!--          </v-container>-->
<!--      </v-card>-->
<!--    </v-container>-->

    <v-snackbar v-model="no_task_snackbar" color="red">
      No tasks available
    </v-snackbar>

  </div>
</template>

<script lang="ts">

import axios from '../../../services/customInstance';
import report_dashboard from '../../report/report_dashboard'
import user_visit_history_list from '../../event/user_visit_history_list.vue'
import project_pipeline from '../../project/project_pipeline'

import Vue from "vue";

export default Vue.extend( {
  name: 'annotator_dashboard_me',
  components: {
    report_dashboard,
    user_visit_history_list,
    project_pipeline,

  },
  data () {
    return {
      no_task_snackbar: false,
      next_task_loading : false,
      resume_task_loading: false,
      last_file: undefined
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
    last_task_event: function (){
      if (!this.$store.state.user.history) { return false }
      let last_task_event = this.$store.state.user.history.find(
        x => x.page_name == 'task_detail')

      this.get_file_with_annotations(last_task_event)

      return last_task_event
    }
  },
  methods: {

    route_resume_task: function(){
      this.resume_task_loading = true
      const routeData = `/task/${this.last_task_event.task_id}`;
      this.$router.push(routeData)
    },

    async get_file_with_annotations(last_task_event) {
        if(!last_task_event){
          return
        }
        let url = '/api/v1/task/' + last_task_event.task_id + '/annotation/list';
        this.get_annotations_error = {}
        this.get_annotations_loading = true
        this.last_file = undefined

        try{
          const response = await axios.post(url, {})
          this.last_file = response.data.file_serialized
        }
        catch(error){
          console.debug(error);
          this.get_annotations_error = this.$route_api_errors(error)
        }
        finally{
          this.get_annotations_loading = false
        }
      return
    },

    api_get_next_task_annotator: async function(){
      try{
        this.next_task_loading = true
        const response = await axios.post(
          `/api/v1/project/${this.project_string_id}/task/next`, {
        });
        if(response.status === 200 && response.data.task){
          let task = response.data.task
          const routeData = `/task/${task.id}`;
          this.$router.push(routeData)
        } else {
          this.no_task_snackbar = true
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

