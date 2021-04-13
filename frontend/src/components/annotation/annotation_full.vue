<template>
  <div style="overflow-x:auto;">

    <div id="annotation_full" tabindex="0">

      <div v-if="images_found == true">


        <v_annotation_core :render_mode=" 'full' "
                           :is_annotation_assignment_bool="false"
                           :project_string_id="project_string_id"
                           :file_id_prop="file_id"
                           @images_found="images_found_function"
                           :request_save="request_save"
                           @save_response_callback="save_response_callback_function"
                           :request_project_change="request_project_change"
                           @current_image="current_image_function"
                           :accesskey="'full'"
                           :file_view_mode="'annotation'"
                           :job_id="job_id"
                           :view_only_mode_prop="view_only"
                           :task_id_prop="task_id_prop"
                           ref="annotation_core"
        >
        </v_annotation_core>


      </div>
      <div v-else>

        <!-- Default if no images uploaded for project -->
        <v-card>
          <v-card-title>
            Welcome!
            Images can be annotated here. :)

          </v-card-title>
          <v-btn @click="upload_link">
            Upload images
          </v-btn>

        </v-card>

      </div>
    </div>
  </div>
</template>


<script lang="ts">

  import axios from 'axios';
  //import annotate from 'diffgram-annotate';
  //console.log(annotate)

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

          // this is a bit awkward...
        }
      },
      created() {
        this.$store.commit('set_project_string_id', this.project_string_id);
        if (this.$route.query.view_only) {
          this.view_only = true;
        }
        if(this.$props.task_id_prop){
          this.add_visit_history_event('task')
        }
        else if(this.$props.file_id_prop){
          this.add_visit_history_event('file')
        }
        else{
          this.add_visit_history_event('page')
        }
      },
      mounted() {
        if (this.$route.query.view_only) {
          this.view_only = true;
        }


      },
      computed: {
        file_id: function(){
          let file_id = this.$props.file_id_prop;
          if(this.$route.query.file){
            file_id = this.$route.query.file;
          }
          return file_id;
        },
        download_annotations_computed: function () {
          if (this.annotation_format == "YAML") {
            return this.url_yaml
          } else {
            return this.url_json
          }
        }
      },
      beforeRouteLeave(to, from, next) {
        if (this.$refs.annotation_core && this.$refs.annotation_core.has_changed) {
          if (!window.confirm("Leave without saving?")) {
            return;
          }
        }
        next();
      },
      methods: {
        add_visit_history_event: async function(object_type){
          let page_name = 'data_explorer'
          if(this.$props.file_id_prop){
            page_name = 'file_detail'
          }
          if(this.$props.task_id_prop){
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
        get_project_string_id: function(){
          if(this.$props.project_string_id){
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

      }
    }
  ) </script>
