<template>
  <v-card v-if="file && file.id" class="pa-1" :elevation="elevation">
    <v-card-title class="pa-0">
      File ID: {{ file.id }}
    </v-card-title>
    <v-container>
      <v-row>
        <v-col cols="12" class="pa-0">
          <p class="ma-0">
            Updated:
            <strong v-if="file.time_last_updated"> <!-- v-if here so moment() doesn't freak out-->
            {{ file.time_last_updated | moment("MMM Do, YYYY H:mm:ss a") }}
            </strong>
          </p>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12" class="pa-0">
          <p>
            Created:
            <strong>
            {{ file.created_time | moment("MMM Do, YYYY") }}
            </strong>
          </p>
        </v-col>
      </v-row>

      <v-row>
        <v-layout column>
          <h5>File Data:</h5>
          <ul>
            <li v-if="file.original_filename">
              Filename: {{ file.original_filename }}
            </li>
            <li >
              Type: {{ file.type }}
            </li>
            <li v-if="file.image">
              Width: {{ file.image.width }} Height: {{file.image.height}}
            </li>
          </ul>

          <!-- Current Video -->
          <div v-if="video.width || video.frame_rate">
            <h5>Video Data:</h5>
            <ul>
              <li>
                Frame Rate: {{ video.frame_rate }}
              </li>
              <li >
                Width, Height: {{ video.width }} , {{video.height}}
              </li>

              <li v-if="video.parent_video_split_duration">
                Split Duration: {{video.parent_video_split_duration}} seconds
              </li>
              <li v-if="video.offset_in_seconds">
                Offset: {{ video.offset_in_seconds }} seconds
              </li>
              <li v-if="!video.offset_in_seconds">
                Video not split.
              </li>
            </ul>
          </div>

        </v-layout>
      </v-row>

    </v-container>
  </v-card>
</template>

<script lang="ts">
  import Vue from "vue";

  export default Vue.extend({
      name: 'file_metadata_card',
      props: [
        'file',
        'video',
        'elevation',
        'project_string_id'
      ],
      data() {
        return {
          loading: false,
          related_tasks: false,
          related_tasks_error: {},
        }
      },
      mounted() {

      },
      methods: {
        go_to_task_new_tab: function(task_id){
          window.open(  `/task/${task_id}`, "_blank");
        },

      }
    }
  ) </script>

<style scoped>
  .file-text{
    font-size: 12px !important;
  }
  .task-link:hover{
    cursor: pointer;
  }
  .task-link{
    border-radius: 25px;
    font-size: 10px;
    white-space: nowrap;
    line-height: 15px
  }
</style>
