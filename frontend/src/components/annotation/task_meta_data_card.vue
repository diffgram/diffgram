<template>
  <v-card v-if="task.id" class="ml-4 ma-2" :elevation="elevation">
    <v-container class="pa-0">
      <div>
        <h3> Task ID: {{ task.id }} </h3>
        <v-layout class="d-flex flex-column">
          <div class="d-flex align-center">
            <p class="ma-0 d-flex">

              <strong>Status:</strong>
              <task_status_icons
                :status="task.status"
                :large="false"
              >
              </task_status_icons></p>


            <!-- We still need to define what happens in terms of the pipeline when uncompleting tasks. -->
            <!--                <tooltip_button-->
            <!--                  tooltip_message="Mark as not completed"-->
            <!--                  v-if="task.status === 'complete'"-->
            <!--                  @click="change_file('previous', 'none')"-->
            <!--                  :loading="loading || annotations_loading"-->
            <!--                  :disabled="loading || annotations_loading || File_list.length == 0"-->
            <!--                  color="warning"-->
            <!--                  icon="mdi-book-remove"-->
            <!--                  :icon_style="true"-->
            <!--                  :bottom="true"-->
            <!--                >-->
            <!--                </tooltip_button>-->
          </div>

          <p >
            <strong>Date Completed:</strong>
            <span v-if="task.time_completed && task.time_completed != 'None'">{{ task.time_completed | moment("MMM Do, YYYY") }}</span>
            <span v-else>N/A</span>
          </p>
          <p v-if="task.job_id">
            <strong>Job ID: </strong>
            <strong ><a class="secondary--text" :href="`/job/${ task.job_id }`"  target="_blank" style="text-decoration: none"><v-icon color="secondary">mdi-open-in-new</v-icon>{{task.job_id}}</a></strong>
          </p>
        </v-layout>
        <v-layout column>
          <h5>File Data:</h5>
          <ul>
            <li v-if="$store.state.job.current && task.job_id == $store.state.job.current.id">
              Job Type: {{$store.state.job.current.type }}
            </li>
            <li v-if="$store.state.job.current && task.job_id == $store.state.job.current.id">
              Job Name: {{$store.state.job.current.name }}
            </li>
            <li v-if="file.original_filename">
              Filename: {{ file.original_filename }}
            </li>
            <!-- v-if here so moment() doesn't freak out-->
            <li v-if="file.time_last_updated">
              Last Updated:
              {{ file.time_last_updated | moment("dddd, MMMM Do H:mm:ss a") }}
            </li>
            <li >
              Type: {{ file.type }}
            </li>
          </ul>

          <!-- Current Video -->
          <h5>Video Data:</h5>
          <ul v-if="video">
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


        </v-layout>

      </div>
    </v-container>
  </v-card>
</template>

<script lang="ts">

  import axios from 'axios';
  import task_status_icons from '../regular_concrete/task_status_icons';

  import Vue from "vue";

  export default Vue.extend({
      name: 'task_metadata_card',
      props: [
        'task',
        'file',
        'video',
        'project_string_id',
        'elevation'
      ],
      components: {
        task_status_icons
      },
      data() {
        return {
        }
      },
      methods: {

      }
    }
  )
</script>

