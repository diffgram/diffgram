<template>
  <!-- Template section for the component's UI -->
</template>

<script lang="ts">
  import axios from '../../services/customInstance';
  import Vue from "vue";
  import _ from "lodash";
  import {get_labels} from '../../services/labelServices';
  import DiffgramExportFileIngestor from "./DiffgramExportFileIngestor";

  export default Vue.extend({
    name: 'diffgram_export_validator',
    components: {}, // Registered components
    props: {
      // Component properties
    },
    data() {
      // Data properties and initial values
    },
    computed: {
      // Computed properties
    },
    watch: {
      // Watched properties
    },
    mounted() {
      // Component mounted lifecycle hook
    },
    created() {
      // Component created lifecycle hook
    },
    destroyed() {
      // Component destroyed lifecycle hook
    },
    beforeDestroy() {
      // Component beforeDestroy lifecycle hook
    },
    methods: {
      // Component methods
    }
  });
</script>

<style>
  /* Component styles */
</style>


<script lang="ts">
  import axios from '../../services/customInstance';
  import Vue from "vue";
  import _ from "lodash";
  import {get_labels} from '../../services/labelServices';
  import DiffgramExportFileIngestor from "./DiffgramExportFileIngestor";

  export default Vue.extend({
    name: 'diffgram_export_validator',
    components: {},
    props: {
      'project_string_id': {
        default: null
      },
      'file_list_to_upload': {
        default: null
      },
      'upload_mode': {
        default: 'new'
      },
      'diffgram_export_ingestor': {
        type: DiffgramExportFileIngestor,
        default: null
      }
    },
    data() {
      return {
        // ...
      }
    },
    computed: {
      all_checks_passed: function(){
        // ...
      }
    },
    watch: {
      // ...
    },
    mounted() {
      // ...
    },
    created() {
      // ...
    },
    destroyed() {
      // ...
    },
    beforeDestroy() {
      // ...
    },
    methods: {
      go_to_wizard_step: function(num){
        // ...
      },
      // ...
    }
  });
</script>
