<template>
  <!-- Root component element -->
  <div>

    <!-- Annotation trainer job info component -->
    <v-annotation_trainer_job_info
      :job_id="job_id" <!-- Pass the job ID prop -->
      @job_info="job = $event" <!-- Emit an event to update the job data -->
    >
    </v_annotation_trainer_job_info>

    <!-- Annotation core component -->
    <v_annotation_core
      :file_id_prop="file_id_prop" <!-- Pass the file ID prop -->
      :request_project_change="request_project_change" <!-- Pass the request project change data -->
      :accesskey="'annotation_trainer'" <!-- Pass the access key -->
      :file_view_mode="'annotation'" <!-- Pass the file view mode -->
      :job_id="job_id" <!-- Pass the job ID prop -->
      :job="job" <!-- Pass the job data -->
    >
    </v_annotation_core>

  </div>
</template>

<script lang="ts">
import Vue from "vue";
export default Vue.extend({
  name: 'annotation_trainer', // Component name
  props: {
    'file_id_prop': { // File ID prop
      default: null
    },
    'job_id': { // Job ID prop
      default: null
    }
  },
  data () {
    return {
      loading: false, // Loading state
      images_found: true, // Images found state
      request_save: false, // Request save state
      request_project_change: null, // Request project change data
      current_image: null, // Current image data
      download_annotations_loading: false, // Download annotations loading state
      annotation_example: false, // Annotation example state
      job: {} // Job data
    }
  },
  watch: {
    '$route'(to, from) { // Watch for route changes
      this.images_found = true
      // this is a bit awkward...
    }
  },
  created() {
    // Component created logic
  },
  computed: {
    // Computed properties
  },
  methods: {
    // Component methods
  }
})
</script>
