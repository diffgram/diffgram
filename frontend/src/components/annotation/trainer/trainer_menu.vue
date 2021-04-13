<template>
  <div v-cloak>
    <v-layout fill-height>

      <button_with_menu         
        tooltip_message="Guide"
        icon="mdi-book-open"
        :close_by_button="true"
        color="green"
        offset="y"
            >

        <template slot="content">
          <v-layout column>

            <div v-if="task.guide">
              {{task.guide.name}}
          
              <VueMarkDown :source="task.guide.markdown">
                </VueMarkDown>

            </div>
         
          </v-layout>
        </template>

      </button_with_menu>

    </v-layout>
  </div>
</template>

<script lang="ts">



import Vue from "vue"; export default Vue.extend( {
  name: 'annotation_trainer_menu',
  props: {
    'job_id': {
      default: null
    },
    'task': {
      default: null
    }
  },
  data() {
    return {
    }
  },
  computed: {

  },

  watch: {

    },

  created() {

  },
  methods: {
  }
}

) </script>
