<template>
  <dataset_new 
    :project_string_id="this.$store.state.project.current.project_string_id"
    @directory_created="directory_created"
  />
</template>

<script lang="ts">
import dataset_new from "../../concrete/dataset/dataset_new.vue"

import Vue from "vue"; export default Vue.extend({
  name: 'dataset_new_and_commit',
  components: {
    dataset_new
  },
  data() {
    return {
      project_string_id: null as string
    }
  },
  mounted() {
    this.project_string_id = this.$store.state.project.current.project_string_id
  },
  methods: {
    directory_created: function(new_directory: object): void {
      this.$store.commit('patch_single_directory', new_directory)
      this.$emit('directory_created', new_directory)
    }
  }
}
) 
</script>
