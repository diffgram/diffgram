<template>
  <div style="overflow-x:auto;">

    <div id="annotation_full" tabindex="0">
      <div v-if="images_found == true">
        <v_annotation_core :render_mode=" 'full' "
                           :is_annotation_assignment_bool="false"
                           :project_string_id="project_string_id"
                           :file_id_prop="file_id"
                           :task="task"
                           :task_id_prop="task_id_prop"
                           :request_save="request_save"
                           :request_project_change="request_project_change"
                           :accesskey="'full'"
                           :file_view_mode="'annotation'"
                           :job_id="job_id"
                           :view_only_mode="view_only_mode"

                           @save_response_callback="save_response_callback_function"
                           @current_image="current_image_function"
                           @images_found="images_found_function"
                           @set_file_list="set_file_list"
                           ref="annotation_core"
        >
        </v_annotation_core>
      </div>
      <div v-else>

        <!-- Default if no images uploaded for project -->
        <v-card>
          <v-card-title>
            Welcome!
            Images/Text can be annotated here. :)

          </v-card-title>
          <v-btn @click="upload_link">
            Upload images
          </v-btn>

        </v-card>

      </div>


      <v_media_core :project_string_id="project_string_id"
                    @change_file="change_file('none', $event)"
                    @remove_file_request="remove_file_request($event)"
                    @request_media="request_media($event)"
                    file_view_mode="annotation"
                    @replace_file="replace_file($event[0], $event[1])"
                    :view_only_mode="view_only_mode"
                    :job_id="job_id"
                    :job="job"
                    :media_loading="media_loading"

                    :visible="media_sheet"
                    @height="media_core_height = $event"
                    ref="media_core"
      >
      </v_media_core>
    </div>
  </div>
</template>


<script lang="ts">
  import axios from 'axios';
  import {create_event} from "../event/create_event";
  import Vue from "vue";

  export default Vue.extend({
      name: 'annotation_full',
      props: {
        'project_string_id': {
          default: null
        },
        'file_id_prop': {
          default: null
        },
        'job_id': {
          default: null
        },
        'task_id_prop': {
          default: null
        },

      },
      data() {
        return {

          loading: false,
          task: false,
          images_found: true,
          request_save: false,
          request_project_change: null,
          view_only: false,
          current_image: null,
          download_annotations_loading: false,
          annotation_example: false,

        }
      },
      watch: {
        '$route'(to, from) {
          this.images_found = true,
            this.request_project_change = Date.now()
        }
      },
      created() {
        this.get_project();
        this.$store.commit('set_project_string_id', this.project_string_id);
        if (this.$route.query.view_only) {
          this.view_only = true;
        }
        if (this.$props.task_id_prop) {
          this.add_visit_history_event('task');
          this.fetch_single_task();
        } else if (this.$props.file_id_prop) {
          this.add_visit_history_event('file');

        } else {
          this.add_visit_history_event('page')
        }
      },
      mounted() {
        if (this.$route.query.view_only) {
          this.view_only = true;
        }
      },
      computed: {
        file_id: function () {
          let file_id = this.$props.file_id_prop;
          if (this.$route.query.file) {
            file_id = this.$route.query.file;
          }
          return file_id;
        },
      },
      methods: {
        fetch_single_task: async function(task_id){
          this.media_sheet = false;
          this.task_error = {
            'task_request': null
          }
          this.loading = true
          this.error = {}   // reset
          this.media_loading = true  // gets set to false in shared file_update_core()
          if(!task_id){
            throw Error('Provide task ID');
          }
          try{
            const response = await axios.post('/api/v1/task', {
              'task_id': parseInt(task_id, 10),
              'builder_or_trainer_mode': this.$store.state.builder_or_trainer.mode
            });
            if (response.data.log.success == true) {

              // TODO what parts of this can be merged with
              // builder traner mode below

              this.ile_list = [response.data.task.file]

              this.task = response.data.task
              this.job_id = this.task.job_id

              if (this.task.task_type == "review" && this.task.job_type == "Exam") {
                this.label_settings.show_list = false

              }

              this.label_file_colour_map = this.task.label_dict.label_file_colour_map
              this.label_list = this.task.label_dict.label_file_list_serialized

              // careful, gold_standard_file default dict has some specific properties
              // the server returns null if there is no file but
              // the front end still needs the default properties
              // especially as vue js renders errors messages in this context in a very cryptic way
              if (response.data.task.gold_standard_file) {
                this.gold_standard_file = response.data.task.gold_standard_file   // careful, under task dict
              }

              this.$emit('file_list_length', this.File_list.length)
            }
            this.task_error = response.data.log.error
            await this.file_update_core()
          }
          catch(error){
            console.debug(error);
            this.loading = false
            // this.logout()
          }
        },
        get_project: function () {

          if (this.project_string_id == null) {
            return
          }

          if (this.project_string_id == this.$store.state.project.current.project_string_id) {
            // context that if we already have the the project, there's not specific need to refresh
            // project is bound / related to directory so if it refresh artifically we need
            // to cache directory
            // Not clear if downsides of not refreshing here by default
            return
          }

          axios.get('/api/project/' + this.project_string_id + '/view')
            .then(response => {
              if (response.data['none_found'] == true) {
                this.none_found = true
              } else {
                //console.debug(response)
                this.$store.commit('set_project_name', response.data['project']['name'])
                this.$store.commit('set_project', response.data['project'])

                // TODO may not be right place to get this
                if (response.data.user_permission_level) {
                  this.$store.commit('set_current_project_permission_level',
                    response.data.user_permission_level[0])

                  if (response.data.user_permission_level[0] == "Viewer") {
                    this.view_only = true
                  }
                }
              }
            })
            .catch(error => {console.debug(error); });
        },
        set_file_list: function(new_file_list){
          this.$refs.media_core.set_file_list(new_file_list)
        },
        add_visit_history_event: async function (object_type) {
          let page_name = 'data_explorer'
          if (this.$props.file_id_prop) {
            page_name = 'file_detail'
          }
          if (this.$props.task_id_prop) {
            page_name = 'task_detail'
          }
          const event_data = await create_event(this.get_project_string_id(), {
            file_id: this.$props.file_id_prop,
            task_id: this.$props.task_id_prop,
            page_name: page_name,
            object_type: object_type,
            user_visit: 'user_visit',
          })
        },
        get_project_string_id: function () {
          if (this.$props.project_string_id) {
            return this.$props.project_string_id;
          }
          return this.$store.state.project.current.project_string_id;
        },
        current_image_function: function (result) {
          this.current_image = result
        },
        request_save_function: function () {
          this.request_save = true
        },
        save_response_callback_function: function (result) {

          if (result == true) {
            this.request_save = false
            // better error handling here?
          }

        },
        upload_link: function () {
          this.$router.push('/studio/upload/' +
            String(this.$store.state.project.current.project_string_id))
        },

        images_found_function: function (bool) {
          this.images_found = bool
        },

        route_annotation_project() {
          this.$router.push('/project/' + String(this.project_string_id) + '/annotation_project/new')

        },

        route_annotation_project_versions() {
          this.$router.push('/project/' +
            String(this.project_string_id) + '/annotation_project/versions')
        }

      },
    }
  )
</script>
