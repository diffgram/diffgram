<template>
  <div v-cloak>

      <!--
     Problem:  both v-alert and v-card Both have tons of issues with controlling width in toolbar setting
     Solution: button component that seems to control width better
    -->

    <!-- Complete File -->
    <tooltip_button
      :tooltip_message="complete_message"
      v-if="!task_id && current_file.ann_is_complete != true && view_only_mode != true"
      @click="is_complete_toggle_file(true)"
      :loading="is_complete_toggle_loading"
      :disabled="is_complete_toggle_loading || disabled"
      color="primary"
      icon="mdi-check-circle-outline"
      :icon_style="true"
      :bottom="true"
                    >
    </tooltip_button>


    <!-- Complete Task -->
    <tooltip_button
      tooltip_message="Complete Task"
      v-if="task && task.id && task.status !== 'complete'"
      @click="is_complete_toggle_task(true)"
      :loading="is_complete_toggle_loading"
      :disabled="is_complete_toggle_loading || disabled"
      color="primary"
      icon="mdi-check-circle-outline"
      :icon_style="true"
      :bottom="true"
    >
    </tooltip_button>

    <regular_chip
      v-if="task && task.status === 'complete'"
      class="pt-2 d-flex align-center"
      message="Complete"
      tooltip_message="Task Status"
      color="success"
      tooltip_direction="bottom">

      <template slot="chip">
        <v-icon dark left> mdi-check-circle </v-icon>
      </template>

    </regular_chip>
    <!-- Just disable, don't show loading while saving,
        it's too distracting to show loading,
        and could confuse user (ie they think they clicked different button)

        Make button smaller in context of videos that
        take a lot of time per video and really don't need such a big
        button.
      -->

    <!-- Already complete -->

    <regular_chip
      v-if="!task && current_file.ann_is_complete == true"
      class="pt-2"
      message="Complete"
      tooltip_message="File Status"
      color="success"
      tooltip_direction="bottom">

      <template slot="chip">
        <v-icon dark left> mdi-check-circle </v-icon>
      </template>

    </regular_chip>

    <tooltip_button
        tooltip_message="Mark File As Not Complete"
        @click="is_complete_toggle_file()"
        v-if="!task && current_file.ann_is_complete == true && !view_only_mode"
        icon="cancel"
        :loading="is_complete_toggle_loading"
        :disabled="is_complete_toggle_loading"
        :icon_style="true"
        color="warning"
        :bottom="true"
                    >
    </tooltip_button>

  </div>
</template>

<script lang="ts">

import axios from 'axios';

import Vue from "vue";

export default Vue.extend( {

  name: 'is_complete',
  props: {'project_string_id' : {},
          'current_file': {},
          'task': undefined,
          'complete_on_change_trigger': {},
          'view_only_mode': {},
          'save_and_complete': {},
          'loading': {
              default: false,
              type: Boolean
          },
          'disabled' : {
              default: false,
              type: Boolean
          },
          'task_id' : {
              default: null,
              type: Number
          }
  },
  data() {
    return {
      is_complete_toggle_loading: false

    }
  },
  computed: {
   complete_message: function () {
      if (this.current_file.video_id){
        return "Complete Video"
      } else {
        return "Complete"
      }
    }
  },

  watch: {
    'complete_on_change_trigger': 'is_complete_toggle'
  },

  created() {

  },
  methods: {
    is_complete_toggle_file: function (on_complete_only=false) {
      // TODO review in context of switching new file for source control
      // (See / combine with above save method for splicing in new file)
      let cache_current_file_id = this.current_file.id
      if (cache_current_file_id == undefined) {
        return
      }

      // save_and_complete prop, ie so only do this when used in menu
      // on_complete_only so "cancel" button doesn't push to next page
      if (this.save_and_complete == true && on_complete_only == true) {
        this.$store.commit('save_and_complete')
        return
      }

      let endpoint = '/api/project/' + this.project_string_id +
        '/file/' + cache_current_file_id +
        '/annotation/is_complete_toggle'

      axios.post(endpoint, {
        directory_id: this.$store.state.project.current_directory.directory_id
      }).then(response => {
        this.is_complete_toggle_loading = false
        this.$emit('replace_file', [response.data.new_file, cache_current_file_id])
      }).catch(error => {

      });
    },
    is_complete_toggle_task: function (on_complete_only=false) {
      // TODO review in context of switching new file for source control
      // (See / combine with above save method for splicing in new file)
      let cache_current_file_id = this.current_file.id
      if (cache_current_file_id == undefined) {
        return
      }
      // save_and_complete prop, ie so only do this when used in menu
      // on_complete_only so "cancel" button doesn't push to next page
      if (this.save_and_complete == true && on_complete_only == true) {
        this.$store.commit('save_and_complete');
        this.$emit('complete_task');
        return
      }
      const endpoint = `/api/v1/task/${this.task_id}/file/is_complete_toggle`

      axios.post(endpoint, {
        directory_id: this.$store.state.project.current_directory.directory_id
      }).then(response => {
        this.is_complete_toggle_loading = false
        this.$emit('replace_file', [response.data.new_file, cache_current_file_id]);

        }).catch(error => {
      });
    }

  }
}

) </script>
