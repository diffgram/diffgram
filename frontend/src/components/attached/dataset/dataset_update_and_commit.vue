<template>
    <dataset_update
        :current_directory_prop="current_directory_prop"
        @directory_created="directory_created"
    />
</template>

<script lang="ts">
import Vue from "vue"; 
import dataset_update from '../../concrete/dataset/dataset_update.vue'

export default Vue.extend( {
  name: 'dataset_update_and_commit',
  components: {
    dataset_update
  },
  props: {
    current_directory_prop: {
        type: Object,
        required: true
    }
  },
  data() {
    return {
        current_directory: {
            nickname: ""
        } as object
    }
  },
  watch: {
    current_directory_prop() {
        this.current_directory = this.current_directory_prop
    }
  },
  mounted() {
    this.current_directory = this.current_directory_prop
  },
  methods: {
    directory_created: function(directory_list: Array<any>, mode: string): void {
        const cached_dataset_id = this.current_directory.directory_id

        const updated_directory = directory_list.find(directory => directory.directory_id === cached_dataset_id)
        
        if (updated_directory) {
            this.$store.commit('set_current_directory', updated_directory)
        } else {
            throw new Error("Could not find directory just updated.")
        }

        if (mode == "ARCHIVE") {
            this.$store.commit('init_media_refresh')
        }
    }
  }
}
) 
</script>
