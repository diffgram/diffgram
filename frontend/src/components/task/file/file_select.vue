<template>
<div v-cloak>

  <!-- See file add for file list (which gets passed from media core -->

  <v_annotation_core :view_only_mode_prop="true"
                      :render_mode=" 'home' "
                      :is_annotation_assignment_bool="false"
                      :project_string_id="project_string_id"
                      :file_view_mode=" 'task' "
                      :accesskey="'changes'"
                      @file_list_length="directory_file_list_length = $event,
                        $emit('directory_file_list_length', $event)"
                      :job="job"
                      :job_id="job_id">
  </v_annotation_core>


</div>
</template>

<script lang="ts">


/*
 * Feb 14, 2020
 * Not clear what value this abstraction provides.
 * Perhaps annotation core should be inside of job new directly?
 *
 */
import directory_icon_selector from '../../source_control/directory_icon_selector'
import Vue from "vue";

export default Vue.extend( {
  name: 'task_file_select',
  props: {
    'project_string_id': {
      default: null
    },
    'job_id': {
      default: null
    },
    'job':{
      default: null
    }
  },
  components:{
    directory_icon_selector
  },
  data() {
    return {
      loading: false,

      summary: null,
      description: null,

      current_file: {
        image: {},
        id: null
      },

      selected: [],

      // careful this is *directory* length not job length
      directory_file_list_length: null

    }
  },
  computed: {

  },
  created() {


  },
  methods: {


  }
}

) </script>
