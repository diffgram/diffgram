<template>
  <div>

    <div id="annotation_trainer" tabindex="0">

      <!-- TODO  Consider putting this somewhere else
          as it takes up a lot of screen real estate.-->
      <v_annotation_trainer_job_info :job_id = "job_id"
                                     @job_info ="job = $event"
                                     >

      </v_annotation_trainer_job_info>


      <v_annotation_core
          :file_id_prop="file_id_prop"
          :request_project_change="request_project_change"
          :accesskey="'annotation_trainer'"
          :file_view_mode="'annotation'"
          :job_id="job_id"
          :job="job"
                         >
      </v_annotation_core>


    
    </div>
  </div>
</template>


<script lang="ts">

import Vue from "vue"; export default Vue.extend( {
  name: 'annotation_trainer',
  props: {

    'file_id_prop': {
      default: null
    },
    'job_id': {
      default: null
    }

  },

  data () {
    return {

      loading: false,
      images_found: true,
      request_save: false,
      request_project_change: null,

      current_image: null,
      
      download_annotations_loading: false,
      annotation_example: false,

      job: {}

    }
  },
  watch: {
    '$route'(to, from) {
      this.images_found = true

      // this is a bit awkward...
    }
  },
  created() {

  },
  computed: {

  },
  methods: {
    

  }
}
) </script>
