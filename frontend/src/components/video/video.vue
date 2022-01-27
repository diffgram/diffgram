<template>
  <div v-cloak style="position:relative;">
    <v-card v-if="video_mode == true && show_video_nav_bar == true"
            :max-height="player_height"
            elevation="1"
            :width="player_width ? player_width: undefined">
      <v-container fluid >

      <v-row :style="{overflow: 'hidden'}" class="pt-2">

        <!-- Previous Frame -->

        <div class="">
          <tooltip_button
              datacy="back_3_frames"
              :disabled="loading || go_to_keyframe_loading || playing || video_current_frame_guess < 3"
              @click.stop="move_frame(-3)"
              icon="mdi-chevron-triple-left"
              tooltip_message="Back 3 Frames"
              color="primary"
              :icon_style="true"
              :bottom="true"
                          >
          </tooltip_button>
        </div>

        <tooltip_button
            datacy="back_1_frame"
            :disabled="loading || go_to_keyframe_loading ||
                        playing || video_current_frame_guess == 0"
            @click="move_frame(-1)"
            icon="mdi-chevron-left"
            tooltip_message="Back 1 Frame (A)"
            color="primary"
            :icon_style="true"
            :bottom="true"
                        >
        </tooltip_button>


        <!-- Play / Pause
          caution padding needs to match play / pause -->
        <div v-show="playing == false">
          <tooltip_button
              datacy="play_button"
              :disabled="play_loading || loading || go_to_keyframe_loading || at_end_of_video"
              @click="video_play"
              icon="play_arrow"
              tooltip_message="Play (Spacebar)"
              color="blue"
              :icon_style="true"
              :bottom="true"
                          >
          </tooltip_button>
        </div>

        <div v-show="playing == true">
            <tooltip_button
              datacy="pause_button"
              @click="video_pause"
              icon="pause"
              tooltip_message="Pause (Spacebar)"
              color="primary"
              :icon_style="true"
              :bottom="true"
                          >
          </tooltip_button>
        </div>


        <!-- Next frame -->
        <tooltip_button
            datacy="forward_1_frame"
            :disabled="loading || go_to_keyframe_loading || playing || at_end_of_video"
            @click="move_frame(1)"
            icon="mdi-chevron-right"
            tooltip_message="Forward 1 Frame (D)"
            color="primary"
            :icon_style="true"
            :bottom="true"
                        >
        </tooltip_button>

        <tooltip_button
            datacy="forward_3_frames"
            :disabled="loading || go_to_keyframe_loading || playing || at_less_than_3_frames_from_end"
            @click="move_frame(3)"
            icon="mdi-chevron-triple-right"
            tooltip_message="Forward 3 Frames"
            color="primary"
            :icon_style="true"
            :bottom="true"
                        >
        </tooltip_button>


        <div class="pl-2">
          <v-tooltip bottom>
            <template v-slot:activator="{ on }">
              <v-chip v-on="on"
                      color="white"
                      text-color="primary">
                {{video_current_frame_guess}}
                / {{video_settings.slider_end}}
              </v-chip>
            </template>
            Frame
          </v-tooltip>
        </div>

        <div class="pl-2">
          <!-- Fixed width so it doesn't bounce around as it goes up-->
          <v-tooltip bottom>
            <template v-slot:activator="{ on }">
              <v-chip v-on="on"
                      color="white"
                      text-color="primary"
                      style="width: 40px"
                      >
                {{current_time}}
              </v-chip>
            </template>
            Time
          </v-tooltip>
          <v-tooltip bottom>
            <template v-slot:activator="{ on }">
              <v-chip v-on="on"
                      color="white"
                      text-color="primary"
                      style="width: 60px"
                      >
                / {{duration}}
              </v-chip>
            </template>
            Duration
          </v-tooltip>
        </div>



      <button_with_menu
        tooltip_message="Go To KeyFrame"
        icon="mdi-arrow-up"
        color="primary"
        :x-small="true"
        :commit_menu_status="true"
        :disabled="loading || go_to_keyframe_loading || playing"
        :close_by_button="true"
            >

        <template slot="content">

          <v-layout>
            <v-text-field label="Go to frame"
                          type="number"
                          v-model.number="user_requested_keyframe">
            </v-text-field>

            <div class="pa-4">
            / {{video_settings.slider_end}}
            </div>
          </v-layout>

          <v-btn :disabled="loading"
                  color="primary"
                  @click="go_to_keyframe(user_requested_keyframe)">
            Go
          </v-btn>

          </template>
      </button_with_menu>

      <button_with_menu
          tooltip_message="More"
          icon="mdi-dots-vertical"
          color="primary"
          :x-small="true"
          :commit_menu_status="true"
          :disabled="loading || go_to_keyframe_loading || playing"
          :close_by_button="true"
              >

          <template slot="content">

            <v-layout>

              <v-flex class="pa-2">
                <v-select dense
                          class="pb-0"
                          label="Speed"
                          :items="playback_rate_options"
                          v-model="playback_rate"
                          :disabled="loading || go_to_keyframe_loading || playing">
                </v-select>
              </v-flex>

            </v-layout>


            <v-layout class="pb-2">

              <tooltip_button
                  :loading="loading"
                  :disabled="go_to_keyframe_loading || playing"
                  @click="next_instance(undefined)"
                  icon="mdi-debug-step-over"
                  tooltip_message="Jump to Next Existing Instance"
                  color="primary"
                  :icon_style="true"
                  :large="false"
                  :bottom="true"
                >
              </tooltip_button>

              <v-spacer> </v-spacer>

              <tooltip_button
                  tooltip_message="Interpolate All Sequences"
                  @click="run_interpolation"
                  icon="filter_none"
                  :bottom="true"
                  :icon_style="true"
                  :disabled="running_interpolation || loading || go_to_keyframe_loading || playing"
                  color="primary">
              </tooltip_button>

              <div>
                <v-btn color="blue darken-1" text
                    href="https://diffgram.readme.io/docs/video-interpolation"
                    target="_blank"
                    icon>
                  <v-icon>help</v-icon>
                </v-btn>
              </div>

            </v-layout>

            </template>
        </button_with_menu>


        </v-row>

      <v-row @mousemove="mousemove_slider"
              :id="`player_video__${current_video.id}`"
               @mouseleave="mouseleave_slider"
               @mouseenter="mouseenter_slider">
          <!--
             *********** High Danger!!! *********
             Slider component number of ticks renders directly impacts performance.
             So if say step is set to video length, and there are 18,000 frames, then
             it tries to render 18,000 tick icons.

             This was resulting in multi second lag while loading images.

             Do NOT 2 way bind this component, we expect the events to update frame number
             We do want to send the current video frame number to this though so that
             It can update as it plays.

          --->
          <v-slider
            ref="slider"
            data-cy="video_player_slider"
            class="pl-4 pr-4 pt-0"

            @end="slider_end(parseInt($event))"
            @change="slide_change(parseInt($event))"
            :disabled="loading
                    || go_to_keyframe_loading
                    || playing
                    || running_interpolation
                    || any_frame_saving"
            :value="video_current_frame_guess"
            :step="video_settings.step_size"
            ticks
            min="0"
            :max="video_settings.slider_end"
            @start="update_slide_start"
                    >
          </v-slider>

        </v-row>

      </v-container>
    </v-card>

    <v-card v-if="video_mode == true">

      <v-alert v-if="playback_info"
                type="warning">
        Playback Issue Detected.
        <ol>
          <li>Try Reloading the Page.</li>
          <li>Log out and log in again.</li>
          <li>Check your internet connection and <a href="https://diffgram.readme.io/docs/minimum-hardware-specs"> Diffgram Minimum Specs. </a></li>
        </ol>
        <br>
        Technical Info:
        <ul>
          <li> Error: <b>{{video_error_message}} </b></li>
          <li> Project: {{$store.state.project.current.project_string_id}} </li>
          <li> VideoFileID: {{current_video_file_id}} </li>
        </ul>
        <br>
        <div v-if="task">
          Task: {{task.id}}
        </div>

        If the issue persists please send your admin a screenshot and run a speed test.
      </v-alert>

      <v-alert v-if="at_end_of_video == true"
                type="info"
                >
        End of Video

        <tooltip_button
            tooltip_message="Restart Video"
            @click="restart_video"
            icon="refresh"
            :icon_style="true"
            color="white">
        </tooltip_button>

      </v-alert>

      <v_error_multiple :error="error">
      </v_error_multiple>

      <v-progress-linear
                v-if="running_interpolation"
                indeterminate
                >
      </v-progress-linear>

      <v-alert  type="info"
                v-if="interpolate_success"
                dismissible
                @input="interpolate_success = false"
                >

        Interpolation report:

      <ul>

        <li v-for="key in Object.keys(interpolate_sequence_log)">


          <div v-if="interpolate_sequence_log[key].has_changes == false">
            {{interpolate_sequence_log[key].label_name}},
            {{interpolate_sequence_log[key].number}}

            No changes.
          </div>

          <div v-else>
            {{interpolate_sequence_log[key].label_name}},
            {{interpolate_sequence_log[key].number}}
            {{interpolate_sequence_log[key].interpolation_description}}
            <v-alert type="error"
                    v-if="interpolate_sequence_log[key].error">

              {{interpolate_sequence_log[key].error}}

            </v-alert>

          </div>

        </li>

      </ul>

      </v-alert>

    </v-card>

    <video ref="video_source_ref"
            :width="0"
            height="0"
            :id="video_primary_id">

      Your browser does not support the video tag.

    </video>

      <frame_previewVue
        v-if="box_client"
        :visible="frame_preview_visible"
        :mouse_x="mouse_x - box_client.left"
        :mouse_y="mouse_y - box_client.top"
        :frame_url="preview_frame_url"
        :refresh="preview_frame_refresh"
        :frame_estimate="preview_frame_final_estimate"
      >
      </frame_previewVue>



  </div>
</template>

<script lang="ts">
// @ts-nocheck

import axios from 'axios';
import frame_previewVue from './frame_preview.vue'
import pLimit from "p-limit";
import Vue from "vue";

export default Vue.extend( {
  name: 'v_video',
    props: {
      'project_string_id': {
        default: undefined
      },
      'current_video': {
        default: undefined
      },
      'video_mode': {
        default: undefined
      },
      'current_video_file_id': {
        default: undefined
      },
      'video_pause_request': {
        default: undefined
      },
      'video_play_request': {
        default: undefined
      },
      'task': {
        default: undefined
      },
      'loading': {
        default: undefined
      },
      'has_changed': {
        default: undefined
      },
      'canvas_width_scaled': {
        default: undefined
      },
      'stop_propagation_for_player': {
        default: undefined
      },
      'video_primary_id': {
        default: undefined
      },
      'player_width': {
        default: undefined
      },
      'player_height': {
        default: undefined
      },
      'update_query_params':{
        default: true
      },
      'user_nav_width_for_frame_previews':{
        default: true
      },
      'parent_save':{
        default: undefined
      },
      'show_video_nav_bar':{
        default: true
      },
      'any_frame_saving':{
          default: false
      }
    },
  components: {
    frame_previewVue
  },
  data() {
    return {

      error: {},
      MAX_NUM_URL_BUFFER: 15,
      mouse_x: null,
      mouse_y: null,
      mouse_page_x: null,
      mouse_page_y: null,
      frame_preview_visible: false,
      at_less_than_3_frames_from_end: false,
      preview_frame_refresh: null,
      preview_frame_final_estimate: null,

      preview_frame_url: null,
      preview_frame_url_dict : {},
      frame_image_buffer: {},
      frame_url_buffer : {},
      preview_frame_loading : false,

      // concc that we don't wish to rely on the html video player for this
      // for reasons described in detect_early_end()
      at_end_of_video: false,

      first_play: false,

      slide_active: false,

      playback_info: false,
      video_error_message: undefined,

      muted: false,

      go_to_keyframe_loading: false,
      play_loading: false,    // maybe should be a "save_loading"...

      user_requested_keyframe: 0,

      get_video_single_image_last_fired: null,
      interpolate_sequence_log: {},
      primary_video: null,

      // .05 is not supported apparently.
      // https://stackoverflow.com/questions/30970920/html5-video-what-is-the-maximum-playback-rate
      playback_rate_options: [.0625, .1, .15, .25, .5, .75, 1, 1.25],


      change_label_from_id: null,
      current_instance_group_id: null,
      current_instance_id: null,

      video_current_frame_guess: 0,
      current_time: 0,
      prior_frame_number: null,

      seek_time: null,
      playing: false,
      playback_rate: 1,

      done_scrubbing: false,
      frame_spacing: 1,
      running_interpolation: false,

      slider_end_cache: null,
      current_instance: {
        id: null,
        image_url_signed: null,
        instance_group_id: null,
        number: null,
        keyframe_list: null
      },

      run_tracking_disabled: true,
      box_client: null,
      run_FAN_disabled: false,
      run_FAN_success: false,
      interpolate_success: false,

      refresh: Date,
      keyframe_watcher:null
    }
  },
  computed: {
    MAX_NUM_IMAGE_BUFFER: function(){
      // This is to ensure we always have the urls available for fetching.
      return this.MAX_NUM_URL_BUFFER - 12;
    },
    video_settings: function () {
      if (this.current_video) {

        let step_size = 1
        if (this.current_video.frame_count > 110) {
          step_size = Math.round(this.current_video.frame_count / 100) - 1
          step_size = Math.max(step_size, 1)
          // CAREFUL if step_size == 0 the slider will return floats / not
          // work as expected, which can cause servere second order effects
          // because we generally expect this to return an int frame number
        }
        return {
          'step_size': step_size,
          'slider_end': Math.round(this.current_video.frame_count / this.frame_spacing) - 1
        }
      } else {
        return {
          'step_size': 1,
          'slider_end': 1
        }
      }
    },
    duration: function () {
       // Not sure why duration isn't available as a prop on video from backend?
       return this.current_video.frame_count / this.current_video.frame_rate
    }
  },
  mounted() {
    if (window.Cypress) {   // only when testing
      window.video_player = this;
    }
      this.keyframe_watcher = this.create_keyframe_watcher()
  },
  watch: {
    'video_pause_request': 'video_pause',
    'video_play_request': 'video_play',
    video_current_frame_guess: function(frame) {
      if (this.playing) return;
      if(!this.video_mode) return;
      if(this.$props.update_query_params){
        this.updateFrameUrl(frame)
      }
    },
  },
  beforeDestroy() {

    this.keyframe_watcher()
    this.video_pause()    // in case video was still playing

  },
  methods: {
    reset_cache(){
      this.preview_frame_url_dict = {};
      this.preview_frame_url = null;
      this.frame_url_buffer = {};
    },
    create_keyframe_watcher(){

      return this.$store.watch(() => {
        return this.$store.state.video.go_to_keyframe_refresh },
         (new_val, old_val) => {
          this.go_to_keyframe(this.$store.state.video.keyframe)
        },
      )
    },

    next_instance: async function(label_file_id){
      try{
        const project_string_id = this.$store.state.project.current.project_string_id;
        const response = await axios.post(
          `/api/v1/project/${project_string_id}/video/${this.current_video_file_id}/next-instance/start/${this.video_current_frame_guess}`,
        {
              label_file_id: label_file_id
             }
          );
        if(response.data.frame_number){
          this.go_to_keyframe(response.data.frame_number)
        }
      }
      catch (error) {
        console.error(error);
      }
      finally {
      }
    },

    mousemove_slider: function (event) {
      this.box_client = event.currentTarget.getBoundingClientRect();
      this.mouse_x = event.clientX
      this.mouse_page_x = event.pageX
      this.mouse_y = event.clientY
      this.mouse_page_y = event.pageY

      this.predict_frame_from_mouse_location()
    },

    mouseleave_slider: function (event) {
      this.frame_preview_visible = false
      // if the prevew is rendered over top then this will keep firing wrongly?
    },

    mouseenter_slider: function(event){
      this.frame_preview_visible = true
    },

    predict_frame_from_mouse_location: function () {
      /* We assume we can use knowledge of width of slider
       *
       * position / slider_end = frame
       * 50% / (500 frames) = frame 250
       *
       * can use step size to work it
       * position is relative to pixel position relative to
       * total size canvas_width_scaled
       * start point (eg detected from left nave?)
       * (postion - offset ) / canvas_width_scaled
       * // can fiddle with it for padding too
       */
      let rect = this.box_client;
      var x = this.mouse_x - rect.left;
      let padding = 16
      if(x < 0){
        return
      }

      let offset = padding;
      if(!this.$props.user_nav_width_for_frame_previews){
        offset = padding;
      }
      if (isNaN(offset)){
        return
      }
      let slider_width = rect.width - (padding * 2)

      let percent_on_slider = (x - offset) / slider_width
      if (isNaN(percent_on_slider)){
        return
      }
      // could also min/max it at 0 and highest frame

      let frame_guess_relative_to_video = percent_on_slider * this.video_settings.slider_end
      let rounded_integer = this.round_nearest_increment(
        frame_guess_relative_to_video, this.video_settings.step_size * 2)

      rounded_integer = Math.min(rounded_integer, this.video_settings.slider_end-1)
      rounded_integer = Math.max(rounded_integer, 0)
      if (isNaN(rounded_integer)){
        return
      }

      this.preview_frame_final_estimate = rounded_integer

      this.get_preview_frame(rounded_integer)

    },

    round_nearest_increment: function (number, increment) {
      return Math.ceil(number / increment ) * increment;
    },

    sleep: function (ms) {
      return new Promise(resolve => setTimeout(resolve, ms))
    },

    save_and_await: async function () {
      /* Context of wanting to make sure save completes before changing the state.
       * Not sure if this is a great way to solve it long term
       * Feels like it's needed to prevent issues in saving process
       *   b) from coding perspecific this feels very cumbersome,
       *    would rather get an event notice / use a more "built in" system.
       *    in part this feels like the continued confusion / issue with
       *    data ownership in vue components. like logically video should be a seperate thing
       *    but the channel between video and annotation core is not great
       */

      if(!this.$props.parent_save){
        return
      }

      await this.$props.parent_save()

      return true

    },

    video_current_frame_guess_update: function () {
      this.$emit('video_current_frame_guess', this.video_current_frame_guess)
    },

    restart_video: function() {
      this.go_to_keyframe(0)
      this.video_play()
    },


    go_to_keyframe: async function (frame) {
      if (this.go_to_keyframe_loading == true) { // swallow spamming
        return
      }
      /* We currently emit frame updates while playing
       * So this way we know if a specific frame is requested.
       * Usually this is in the context of a user request.
       *
       * This MUST fire before we push new keyframe.
       *
       * Add the 200 ms saving delay (IF changes) till we can better test
       * or better architect this.
       *
       * */

      frame = parseInt(frame) // edge cases

      this.go_to_keyframe_loading = true
      const save_and_await_result = await this.save_and_await();
      this.$emit('go_to_keyframe_loading_started')
      if (save_and_await_result == false) {

        this.go_to_keyframe_loading = false
        return

      } else {

        // assume for now if valid to run this then not at end of video.
        this.at_end_of_video = false

        this.video_current_frame_guess = frame
        // TODO how we want to push this back to annotations component?
        //this.show_annotations = false
        this.$emit('go_to_keyframe');

        this.detect_end_from_keyframe()

        this.push_key_frame()

        await this.get_video_single_image(this.video_current_frame_guess)
      }
      this.updateFrameUrl(frame);
      this.go_to_keyframe_loading = false;
    },

    detect_end_from_keyframe: function () {
      /*
       * ie in the context of a go to keyframe (nothing to do with video playing)
       * seperate function in case we change this later
       */

      if (this.video_current_frame_guess >= this.video_settings.slider_end) {
        this.at_end_of_video = true
      }
      else{
        this.at_end_of_video = false;
      }


      if((this.current_video.frame_count - 3) <= this.video_current_frame_guess ){
        this.at_less_than_3_frames_from_end = true;
      }
      else{
        this.at_less_than_3_frames_from_end = false;
      }

    },

    update_current_frame_guess: function () {

      // frame_rate is the modified frame rate
      // so we just use the straight time
      // where as when we got to a keyframe, we need to convert back to original time
      this.video_current_frame_guess = Math.floor(
        this.primary_video.currentTime * this.current_video.frame_rate)
      this.$emit('video_current_frame_guess', this.video_current_frame_guess)
    },

    push_key_frame: function () {

      if (this.current_video.frame_count == 0) {
        return
      }
      if(!this.primary_video){
        return;
      }

      // TODO, just use "original frame rate" instead of doing multiplication here?
      // fps_conversion_ratio ie == 6, if original fps was 30 and new is 5 (original / actual fps)
      // defaults to 1 ie no change
      // ie if current frame is 5 and original frame rate is 30, we are a time 5/30
      // Becuase this is firing for every frame? Feel it's not clear why we need this
      this.primary_video.currentTime = this.video_current_frame_guess / (this.current_video.frame_rate * this.current_video.fps_conversion_ratio)
      this.current_time = Math.round(this.primary_video.currentTime * 100) / 100

      // Caution this should always execute after current time since the current time will effect it
      /* Manual test
       * ie for task/4256
       * go to frame 1799
       * go to next frame
       * expect it to end video
       * go to previous frame
       * expect it to 'start' / be able to play video.
       *
       */
      this.detect_early_end(this.current_video.parent_video_split_duration)

      this.html_image = this.primary_video
      this.refresh = Date.now()
    },

    move_frame: function(direction) {
      // direction is an int where:
      // -1 to go back, 1 go forward
      let new_frame = this.video_current_frame_guess + direction
      this.go_to_keyframe(new_frame)
      // Better reuse of existing go to keyframe function.

    },

    slide_change: function (event) {
      this.update_slide_start() // saveing hook
      this.slider_end(event)
    },
    update_slide_start: async function () {
      await this.save_and_await();
      this.slide_active = true
      this.$emit("seeking_update", true)
      if (typeof this.video_current_frame_guess != "undefined") {
        this.$emit('slide_start')
      }

    },
    slider_end: function (frame_number) {

      this.slide_active = false

      // end fires twice strangely so this checks that
      this.$emit("seeking_update", false)

      frame_number = parseInt(frame_number) // We expect it to be Int like

      if (frame_number != this.slider_end_cache) {
        this.$emit('go_to_keyframe_loading_started')
        this.slider_end_cache = frame_number
        this.video_current_frame_guess = frame_number
        if (typeof this.video_current_frame_guess != "undefined") {
          this.get_video_single_image(frame_number)
        }
        // assume this will be valid for now.
        this.at_end_of_video = false
      }
    },
    update_from_slider: function (frame_number: number) {
      /*
       * Other events can cause slider to fire.
       * So we catch this here. We only want to do this update path if
       * it's "actually" from slider.
       * Caution need to test both next/previos frame and play
       *
       */
      if (!this.slide_active) {
        return
      }
      frame_number = parseInt(frame_number) // We expect it to be Int like
      // input fires somewhat "random" events so this is an extra catch
      if (isNaN(frame_number) == false) {
        this.video_current_frame_guess = frame_number
        this.show_annotations = false
        this.push_key_frame()
      }
    },

    video_play: async function () {
      /*
       * Some good patterns here
       * https://developers.google.com/web/updates/2017/06/play-request-was-interrupted
       * (including fetching in advance)
       * TODO review the fetch and play example
       */


      /*
       *   Jan 23, 2020
       *   Green screen issue
       *
       *  Temp workaround for longer video
       *  seem to need to reset to 0 to avoid potential buffering
       *  issues.
       *
       *  This fix seems to work,
       *  although needs a further implementation review
       *
       *  We technically changed playPromise to be a  this. too,
       *  but in browser controls setting to 0 is what fixes it
       *  and that seems better a hard reload to null
       *
       *  TODO test without the this.
       *  and also see if having playPromise as part of data to begin
       *  with helps...
       *
       *  NOTE this only seems to be an issue on 4k
       *  videos as of time of writing.
       *
       *  Details planned to be consolidated here:
       *  https://docs.google.com/document/d/1jZwKsHqzkuXMw9j8vVwdXAd_Kt6JZZiLZmtdHocW6Ng/edit#heading=h.fbzi8nmnh88v
       *
       */

      // Feb 24, 2020
      // only do this for high resolution media

      if (!this.primary_video) {
        // refresh if primary video ref doesn't exist
        // usually this should only be for debugging / hot reload purposes
        // alternative is every hot reload makes video fail
        await this.current_video_update()
      }

      this.play_loading = true

      if (await this.save_and_await() == false) {
        this.play_loading = false
        return

      } else {

        if (this.current_video.width > 1920) {
          this.primary_video.currentTime = 0
        }

        this.first_play = false

        this.primary_video.muted = this.muted

        this.playPromise = this.primary_video.play()

        this.play_loading = false
        if (this.playPromise !== undefined) {
          this.playPromise.then(_ => {
            // Automatic playback started!
            // Show playing UI.

            this.playing = true
            this.playback_info = false // reset
            this.video_error_message = undefined

            this.primary_video.currentTime = this.video_current_frame_guess / this.current_video.frame_rate


            this.$emit('playing')
            this.primary_video.playbackRate = this.playback_rate
            this.video_animation_start()

          })
          .catch(error => {
            // Auto-play was prevented
            // Show paused UI.
            // TODO treat 403 / permissions errors differently

            this.playback_info = true
            this.$emit('video_play_failed')
            this.video_error_message = error.message
            // throw new error for sentry IO capturing benefit
            // context of trying to get understanding of what client side issue
            // is happening
            // TODO would like to add a custom tag here like 'video_play'
            // to make this easier to find in sentry
            throw new Error(error)

          });
        }
      }

    },

    // udacity intro on it https://www.youtube.com/watch?v=YGR8rVT6xJ8
    // https://stackoverflow.com/questions/10735922/how-to-stop-a-requestanimationframe-recursion-loop
    // https://stackoverflow.com/questions/38709923/why-is-requestanimationframe-better-than-setinterval-or-settimeout

    video_animation_start: function () {
      https://developer.mozilla.org/en-US/docs/Web/API/window/requestAnimationFrame
      this.animation_request = window.requestAnimationFrame(this.video_animation_unit_of_work)
      // returns a type long, a request id value
      // we can pass that to cancel to cancel animation
      // TODO clarify it's ok we reuse this.animation_request in this way

    },

    video_animation_stop: function () {

      window.cancelAnimationFrame(this.animation_request)

    },

    video_animation_unit_of_work: function (time_from_animation) {

      this.$emit('video_animation_unit_of_work', this.primary_video)

      this.update_current_frame_guess()
      this.current_time = Math.round(this.primary_video.currentTime * 100) / 100
      this.detect_early_end(this.current_video.parent_video_split_duration)

      // TODO better logging of this type of info
      // ie retrying if can't load etc...
      // https://www.w3schools.com/tags/av_prop_networkstate.asp
      // integer codes for state...

      // must be at end?
      this.video_animation_start()
    },

	/**
		* @vue-event {Number} fr - Updates the ?frame=x query param in URL
		*/
    updateFrameUrl(frame) {
      if(!this.$props.update_query_params){
        return
      }
      // update the url w/ current frame if we are viewing a task
      if ((this.task && this.task.id) || this.$props.current_video_file_id) {
         this.$addQueriesToLocation({frame});
      }
    },

    video_pause: function () {

      this.playing = false
      if(this.primary_video){
        this.primary_video.pause()
      }

      this.$emit('pause')

      this.video_animation_stop()

      if (typeof this.video_current_frame_guess != "undefined") {
        this.get_video_single_image(this.video_current_frame_guess)
      }

      this.updateFrameUrl(this.video_current_frame_guess);
    },

    detect_early_end: function (early_end_time) {
      /*
       * Context that we may wish to end at an earlier time
       * then the literal video file ends.
       * At time of writing this was because the split feature may create
       * a few seconds of extra data at the end.
       *
       * More generally this could be useful pattern to detect
       * certain events in video and pause.
       * ie perhaps play "up to next instance"
       * or "stop at next item to review".
       * (this would be slightly different)
       *
       *
       *  Manual check here is to:
       *    * Load a video with known duration is longer then it should be
       *    * Start video prior to split time, ie 59 seconds
       *    * Confirm video stops as expected.
       *
       *  CAUTION We assume that current_time is **accurate to 2 decimal places***
       *    otherwise can have issues if go back single keyframe
       *    (ie timestamp rounds to 60 but frame granularity is higher)
       *
       *    Other case is to check a video that
       *    does not have a duration / early end time.
       *
       */
      if (early_end_time) {
        if (this.current_time >= early_end_time) {
          this.video_end()
        }
      }

    },

    video_end: function () {
      /* Same concepts as video pause in general
       * but with slight differences
       *
       */

      this.video_pause()

      this.at_end_of_video = true

    },

    build_frame_endpoint_multi_permissions(){

      // We use task id being present (instead of builder trainer mode
      // because a builder may still be reviewing a task.)

      let url = ""
      if (this.task && this.task.id) {
        url += '/api/v1/task/' + this.task.id
        }
      else {
        url += '/api/project/' + this.$store.state.project.current.project_string_id
      }

      // use parent file
      url += '/video/single/' + this.current_video_file_id + '/frame-list/'

       return url
    },
    get_next_n_frames: function(frame_number, n){
      // Get next n frame that are still not in the frame url buffer
      const frame_list = []
      for(let i = frame_number; i < this.current_video.frame_count; i++){
        // We assume generally that we will break on n and n is small
        // so we don't really expect to iterate through the entire count
        if(this.frame_url_buffer[i]){
          continue
        }
        else{
          frame_list.push(i)
        }
        if(frame_list.length === n){
          break
        }
      }
      return frame_list
    },
    get_previous_n_frames: function(frame_number, n){
      // Get previous n frame that are still not in the frame url buffer
      const frame_list = []
      for(let i = frame_number; i >= 0; i--){
        if(this.frame_url_buffer[i]){
          continue
        }
        else{
          frame_list.push(i)
        }
        if(frame_list.length === n){
          break
        }
      }
      return frame_list
    },
    add_new_previews_to_buffer: async function(frame_list){
      const url_list = await this.fetch_next_frames(frame_list); // TODO: might change to another endpoint for preview images in future.
      // Populate preview url buffer
      url_list.forEach(url_element => {
        this.preview_frame_url_dict[url_element.frame_number] = url_element.url
      })
    },
    add_new_frame_list_to_buffer: async function(frame_list){
      const url_list = await this.fetch_next_frames(frame_list);
      // Populate frame url buffer
      url_list.forEach(url_element => {
        this.frame_url_buffer[url_element.frame_number] = url_element.url
      })
    },
    fetch_next_frames: async function(frame_list){
      let endpoint_url = this.build_frame_endpoint_multi_permissions()
      try{
        const response = await axios.post(
            endpoint_url, {frame_list:frame_list})
        const url_list = response.data.url_list;
        return url_list;
      } catch(error){
        this.error = this.$route_api_errors(error)
      }
    },
    get_missing_frames_ahead: function(frame_number, n){
      /*
      * Checks if a frame between the given number is and frame_number + n missing. Returns -1 if all frames exists and
      * the missing frame number else.
      * */
      for(let i = frame_number; i <= frame_number + n ; i++){
        if(i >= 0 && i < this.current_video.frame_count){
          if(!this.frame_url_buffer[i]){
            return i
          }
        }
      }
      return -1

    },
    get_preview_frame: async function (frame_number) {


      if (isNaN(frame_number)) { return }

        this.error = {}

        if (this.preview_frame_url_dict[frame_number]){
          this.preview_frame_url = this.preview_frame_url_dict[frame_number]
          this.preview_frame_refresh = Date.now()
          // may have been different issue but good to have something that changes if URL is the same

          return
        }
        else{
          if (this.preview_frame_loading) {
            return}
          this.preview_frame_loading = true
          try{
            // We only get single frame due to preview images being widely spaced
            // And that when we go to a full frame we load the full list anyway
            await this.add_new_previews_to_buffer([frame_number]);
            this.preview_frame_url = this.preview_frame_url_dict[frame_number];
            this.preview_frame_loading = false;
          } catch(error){
            this.error = this.$route_api_errors(error)
            this.preview_frame_loading = false;
            console.error(error);
          }

        }



    },
    fetch_image_from_url: function (src, frame_num) {
      return new Promise((resolve, reject) => {
        if(!src){
          resolve(undefined)
        }

        let image = new Image();
        image.src = src;
        if (process.env.NODE_ENV === "testing") {
          image.crossOrigin = "anonymous";
        }
        image.onload = () => resolve({image: image, frame_num: frame_num});
        image.onerror = reject;
      });
    },
    range: function(start=0, end=null, step=1) {
      if (end == null) {
        end = start;
        start = 0;
      }
      let result = []
      if(start <= end){
        for (let i=start; i < end; i+=step) {
          result.push(i)
        }
      }
      else{
        for (let i=start; i >= end; i-=step) {
          result.push(i)
        }
      }


      return result
    },
    fetch_next_images: async function(frame_number){
      let next_frames = this.range(frame_number, frame_number + this.MAX_NUM_IMAGE_BUFFER, 1)
      let prev_frames = this.range(frame_number, frame_number - this.MAX_NUM_IMAGE_BUFFER, 1);
      next_frames.filter(frame => frame <= this.current_video.frame_count)
      prev_frames.filter(frame => frame >= 0)
      let frames_to_fetch = []
      if(frame_number === 0){
        frames_to_fetch = [...next_frames];

      }
      else{
        frames_to_fetch = [...prev_frames, ...next_frames];
      }

      // Get current frames with no images
      let frames_with_no_image = [];
      for(let frame of frames_to_fetch){
        if(!this.frame_image_buffer[frame]){
          frames_with_no_image.push(frame)
        }
      }

      if(frames_with_no_image.length > 0) {
        try {
          const limit = pLimit(25); // 25 Max concurrent request.
          const promises = frames_with_no_image.map((frame_num) => {
            return limit(() => {
              let url = this.frame_url_buffer[frame_num];
              return this.fetch_image_from_url(url, frame_num)
            });
          });
          let new_images_responses = await Promise.all(promises);
          for (let result of new_images_responses){
            if(result){
              this.frame_image_buffer[result.frame_num] = result.image
            }
          }
        } catch (e) {
          console.error(e)
        }
      }

    },
    get_video_single_image: async function (frame_number) {
      if (isNaN(frame_number)) { return }
      // hacky work around so file update doesn't file twice
      // Careful! If it seems like this 'event' doesn't randomly
      // fire it may actually be this
      // some more to think about here ie in terms of loading etc.
      if (this.get_video_single_image_last_fired &&
         new Date().getTime() < 10 + this.get_video_single_image_last_fired
        ) {
        return
      }
      console.log('get_video_single_image')
      this.get_video_single_image_last_fired = new Date().getTime()

      this.video_current_frame_guess_update()
      const next_frames = this.get_next_n_frames(frame_number, this.MAX_NUM_URL_BUFFER)
      const prev_frames = this.get_previous_n_frames(frame_number, this.MAX_NUM_URL_BUFFER)
      const all_new_frames = [...new Set(next_frames.concat(prev_frames))];
      if (frame_number != this.prior_frame_number) {
        console.log('frame_number != this.prior_frame_number')
        if(!this.frame_url_buffer[frame_number]){
          this.error = {}
          try{
            await this.add_new_frame_list_to_buffer(all_new_frames);
            const new_url = this.frame_url_buffer[frame_number]
            this.go_to_keyframe_loading = false

            this.refresh = Date.now()

            this.prior_frame_number = frame_number
              this.$emit('go_to_keyframe_loading_ended', new_url, frame_number)
          }
          catch(error){

            // Soft fail, ie can't get image and just want to annotate
            // of of video screen
            /* Context that on first load if it fails then need to "play" it to get first frame
             */
            if (this.first_play == true){
              this.muted = true   // required otherwise chrome won't auto play
              this.video_play()
            }

            this.go_to_keyframe_loading = false
            this.error = this.$route_api_errors(error)
              this.$emit('go_to_keyframe_loading_ended', undefined, frame_number)
          }
          finally {

              this.$emit('set_canvas_dimensions')
              this.$emit('update_canvas');
          }
        }
        else{
          const new_url = this.frame_url_buffer[frame_number]
          this.go_to_keyframe_loading = false
          this.refresh = Date.now()

          this.prior_frame_number = frame_number
          const missing_frame = this.get_missing_frames_ahead(frame_number, 5);
          if(missing_frame != -1){
            const next_frames = this.get_next_n_frames(missing_frame, 15)
            const prev_frames = this.get_previous_n_frames(missing_frame, 15)
            const lookahead_frames = [...new Set(next_frames.concat(prev_frames))];
            // We don't add await here because we don't want this to block the function call.
            // It should be a background fetch.
            this.add_new_frame_list_to_buffer(lookahead_frames);
          }
          this.$emit('go_to_keyframe_loading_ended', new_url, frame_number)
          this.$emit('set_canvas_dimensions')
          this.$emit('update_canvas');
        }

        // Proactively fetch next frames
        await this.fetch_next_images(frame_number);


      }



    },

    current_video_refresh: function () {
      this.error = {}
      // this is not great here as now media component will be out of sync...
      axios.get('/api/project/' + this.project_string_id
        + '/video/single/' + this.current_video.id + '/view')
        .then(response => {
          if (response.data.success = true) {

            this.current_video = response.data.current_video
            this.$store.commit('set_video_current', this.current_video)
          }
        }).catch(error => {
          this.error = this.$route_api_errors(error)
        })
    },

    current_video_update: async function () {

      if (typeof this.current_video != "undefined") {

        this.first_play = true    // reset, 4k issue

        this.preview_frame_url_dict = {} // reset cache

        this.primary_video = document.getElementById(this.$props.video_primary_id)

        // https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement/ended_event
        this.primary_video.addEventListener('ended', this.video_end)

        //this.$store.commit('set_video_current', this.current_video)

        this.prior_frame_number = -1 // todo this is not great

        // doesn't work to do playbackRate here...
        /*
        if (this.current_video.frame_rate >= 20) {
          this.playback_rate = .5
        }
        */
        // until we send original frame rate? just default this to be slower
        this.playback_rate = .25

        //this.$refs.video_source_ref.poster = this.current_video.preview_image_url
        // is this needed since we are getting image right away for video?

        // this.current_video.current_frame = 0 // or could be where left off?

        if (this.current_video.frame_count != 0) {
          let frame = 0;
          if(this.$props.update_query_params){
            frame = parseInt(this.$route.query.frame || 0);
          }

          await this.go_to_keyframe(frame);
          if(this.$refs.video_source_ref){
            this.$refs.video_source_ref.src = this.current_video.file_signed_url;
          }

        }
        this.$emit('update_canvas');
      }
    },

    change_instance_request: function (instance) {

      //  this.current_label doesn't exist?

      this.current_instance = instance
      if (this.current_instance.label_id != this.current_label.id) {
        this.change_label_from_id = this.current_instance.label_id
      }
      this.current_instance_group_id = instance.instance_group_id // TODO maybe instance group is a dict
      this.current_instance_id = instance.id
    },
    new_instance_request: function (instance_group) {
      // should this be done server side...
      let instance = {
        number: instance_group.number + 1,
        label_id: instance_group.label.id,
        new: true
      }
      this.change_instance_request(instance)
      for (let i in this.current_video.instance_group_list) {
        if (this.current_video.instance_group_list[i].id == instance_group.id) {
          this.current_video.instance_group_list[i].number = instance.number
          this.current_video.instance_group_list[i].instance_list.splice(0, 0, instance)
        }
      }
    },
    run_interpolation() {
      this.running_interpolation = true

      let url = ""

      if (this.task && this.task.id) {
         url += "/api/walrus/task/" + this.task.id + '/video/interpolate'
      }
      else {
        url += '/api/walrus/project/' + this.project_string_id
        + '/video/single/' + this.current_video_file_id + '/interpolate'
      }

      axios.post(url, {

            // only needed for by project method
            directory_id : this.$store.state.project.current_directory.directory_id

        })
        .then(response => {
          if (response.data.success = true) {
            this.running_interpolation = false
            this.interpolate_success = true
            this.interpolate_sequence_log = response.data.log.sequence

            this.$store.commit('refresh_video_buffer')  // refresh instances

          }
        }).catch(e => {
          this.running_interpolation = false
          console.error(e)
        })
    },
    run_tracking() {
      this.run_tracking_disabled = true
      axios.post('/api/project/' + this.project_string_id
        + '/video/single/' + this.current_video.id + '/track', {

        })
        .then(response => {
          if (response.data.success = true) {
            this.run_tracking_disabled = false

          }
        }).catch(e => { console.error(e) })
    },
    run_FAN() {

      this.run_FAN_disabled = true

      axios.post('/api/project/' + this.project_string_id
               + '/video/' + this.current_video_file_id
               + '/inference/add',
      {})
        .then(response => {
          if (response.data.success = true) {
            this.run_FAN_success = true
          }

          // Until we have better system
          //this.run_FAN_disabled = false
        }).catch(e => {
          console.error(e)
          this.run_FAN_disabled = false
        })

    },

  }
}

) </script>
