<template>
  <div v-cloak >
    <v-card v-if="video_mode == true"
            max-height="80"
            elevation="1"
            >
      <v-container class="pa-2">

      <v-row
            style="height: 40px; overflow: hidden"
            class="pt-2">

        <!-- Previous Frame -->

        <div class="pl-3">
          <tooltip_button
              datacy="back_3_frames"
              :disabled="loading || go_to_keyframe_loading || playing || video_current_frame_guess < 3"
              @click="move_frame(-3)"
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


        <v-spacer> </v-spacer>

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
            class="pl-4 pr-4 pt-0"
            @input="update_from_slider(parseInt($event))"
            @end="slider_end(parseInt($event))"
            @change="slide_change(parseInt($event))"
            :disabled="loading
                    || go_to_keyframe_loading
                    || playing
                    || running_interpolation"
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


    <!-- Move alerts outside of the other panel for seperate sizing -->
    <v-card v-if="video_mode == true">

      <v-alert v-if="playback_info"
                type="warning">
        {{ playback_info }}
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

      <!-- @input is for dismiss issue
        in prior context it just worked.
        -->

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

    <!-- This is purpusely outside of v-card tag
      so that it's always available, ie no race condition with v-if
      and add event listener on this id-->

    <video ref="video_source_ref"
            :width="0"
            height="0"
            id="video_primary">

      Your browser does not support the video tag.

    </video>

    <frame_previewVue
      :visible="frame_preview_visible"
      :mouse_x="mouse_x"
      :mouse_y="mouse_y"
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

import Vue from "vue";

export default Vue.extend( {
  name: 'v_video',
    props: [
    'project_string_id',
    'current_video',
    'video_mode',
    'current_video_file_id',
    'render_mode',
    'video_pause_request',
    'video_play_request',
    'task',
    'loading',
    'has_changed',
    'canvas_width_scaled'
    ],
  /* Careful, we want annotation_core to still make use of the files
   * for images, so we don't want to get confused between current_file
   * and the special case of video
   *
   *
  */
  components: {
    frame_previewVue
  },
  data() {
    return {

      error: {},

      mouse_x: null,
      mouse_y: null,
      frame_preview_visible: false,
      at_less_than_3_frames_from_end: false,
      preview_frame_refresh: null,
      preview_frame_final_estimate: null,

      preview_frame_url: null,
      preview_frame_url_dict : {},
      frame_url_buffer : {},
      preview_frame_loading : false,

      // concc that we don't wish to rely on the html video player for this
      // for reasons described in detect_early_end()
      at_end_of_video: false,

      first_play: false,

      slide_active: false,

      playback_info: null,

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
      run_FAN_disabled: false,
      run_FAN_success: false,
      interpolate_success: false,

      refresh: Date,
      keyframe_watcher:null
    }
  },
  computed: {
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

      this.keyframe_watcher = this.create_keyframe_watcher()

  },
  watch: {
    'video_pause_request': 'video_pause',
    'video_play_request': 'video_play',
    video_current_frame_guess: function(frame) {
      if (this.playing) return;
      if(!this.video_mode) return;
      this.updateFrameUrl(frame)
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
      this.mouse_x = event.clientX
      this.mouse_y = event.clientY

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
      let padding = 16
      if (!this.$store.state.user.settings.studio_left_nav_width){
        this.$store.commit('set_user_setting', ['studio_left_nav_width', 350])
        console.log("error, studio_left_nav_width is unavailable")
      }
      let offset = padding + this.$store.state.user.settings.studio_left_nav_width
      // guess declaritive is ok here
      if (isNaN(offset)){
        console.log("offset is NaN")
        return
      }

      let slider_width = this.canvas_width_scaled - (padding * 2) // CAREFUL this is padding not step size
      let percent_on_slider = (this.mouse_x - offset) / slider_width
      // eg roughly between range 0 - > 1
      if (isNaN(percent_on_slider)){
        console.log("percent_on_slider is NaN")
        return
      }
      // could also min/max it at 0 and highest frame

      let frame_guess_relative_to_video = percent_on_slider * this.video_settings.slider_end
      let rounded_integer = this.round_nearest_increment(
        frame_guess_relative_to_video, this.video_settings.step_size * 2)
      // multiple (eg 2x) because normally step size more aggressive then preview thats needed

      rounded_integer -= 3 // magic adjustment

      rounded_integer = Math.min(rounded_integer, this.video_settings.slider_end-1)
      rounded_integer = Math.max(rounded_integer, 0)

      if (isNaN(rounded_integer)){
        console.log("rounded_integer is NaN")
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
       *
       *   a) from user perspective feel like should be able to save "behind the scences" and let
       *    the user go to next, this creates an artifical block in cases
       *   b) from coding perspecific this feels very cumbersome,
       *    would rather get an event notice / use a more "built in" system.
       *    in part this feels like the continued confusion / issue with
       *    data ownership in vue components. like logically video should be a seperate thing
       *    but the channel between video and annotation core is not great
       *
       * CAUTION
       *  Also, functions that use this need to have 'async' keyword
       *  and needs to be wrapped to block properly...
       *  if (await this.save_and_await() == false) { // failure }
       *  else { // normal code }
       *
       *  Context of sequence creation issues
       *  https://app.hubspot.com/live-messages/5238859/inbox/300479634#reply-editor
       *
       *  UPDATE
       *    Realized that this is basically an "anti pattern" in that part of the whole goal
       *    of JS here is to be non blocking...
       *    so really should be able to quickly cache and save a frame , and then however long it takes on server it's fine...
       *
       */

      this.$emit('request_save')

      if (this.has_changed == true) {
        await this.sleep(200) // give it a chance to save / fire off thing
        console.log("paused")
      }

      return true

      /*
      for (let i = 0; i < 100 ; i++) {   // has changed also covers other saving methods?

        if (this.has_changed == false) {
          // changes saved, break out of waiting
          break
        }
        await this.sleep(100)
        //console.log("waiting", this.has_changed)
      }

      if (this.has_changed == true) {
          return false
      }
      return true
    */
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
      /* Not sure why we weren't relying on that "loading" thing before... maybe because that
       * "get image single" can get called from a different thing? And we wanted to make sure
       * it got the "last" image? Maybe we just had that (other) catch thing in wrong place
       */
      /* We currently emit frame updates while playing
       * So this way we know if a specific frame is requested.
       * Usually this is in the context of a user request.
       *
       * This MUST fire before we push new keyframe.
       *
       * Add the 200 ms saving delay (IF changes) till we can better test
       * or better architect this.
       *
       * ie A) we could check if has_changed becomes false
       *  or B) we could cache the data in some other way so we are more confident about
       *    going to next frame while "old" data is saved.
       *
       * Structurely it's probably good to have has_changed here,
       * Then if we keep watching has_changed, if it fails to change,
       * we could prevent the keyframe change from happening.
       *
       *
       *  1) checking if "safe" to advance to frame should come first
       *  2) would really prefer to get a callback notice when the save event happens
       *  but not 100% clear how to do this so using a loop here for now.
       */

      frame = parseInt(frame) // edge cases

      this.go_to_keyframe_loading = true
      const save_and_await_result = await this.save_and_await();
      if (save_and_await_result == false) {

        this.go_to_keyframe_loading = false
        return

      } else {
        //console.log("fired")

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
      //console.log("push frame called")

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
    update_slide_start: function () {

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
        this.slider_end_cache = frame_number
        this.video_current_frame_guess = frame_number
        //console.log("Slide end")
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

    test_fail_video_src: function () {
      /*
       * Trying to move this to spec.js
       * but need to do more mocking
       */

      this.current_video_update() // reset for dev...

      this.$refs.video_source_ref.src = null
      this.video_play()

      // this part is not quite right yet...
      setTimeout(console.assert(this.playback_info), 1000)


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
      //console.log("this.primary_video.currentTime", this.primary_video.currentTime)

      // Feb 24, 2020
      // only do this for high resolution media


      if (!this.primary_video) {
        // refresh if primary video ref doesn't exist
        // usually this should only be for debugging / hot reload purposes
        // alternative is every hot reload makes video fail
        this.current_video_update()
      }

      this.play_loading = true

      if (await this.save_and_await() == false) {
        this.play_loading = false
        return

      } else {

        //console.log("fired")

        /* Experiment that issue only seems to be on first load
         *
         */

        if (this.current_video.width > 1920) {
          this.primary_video.currentTime = 0
        }

        this.first_play = false

        this.primary_video.muted = this.muted

        this.playPromise = this.primary_video.play()

        /* Jan 8, 2020
         * Added the basic detection if it failed to load or not
         * And show error message.
         * Probably a lot more we could be doing here but maybe build
         * better testing thing first.
         *
         * Was just doing basic testing by opening annotatino core in dev
         * tools and running: (assuming it's 3rd file)
         * $vm0.File_list[3].video.file_signed_url = "https"
         *      (Or = null should work too)
         *
         * We emit the event but it's not really
         * clear what annotation_core should do in terms of locking it,
         * the "loading" thing spining just looks funny...
         *
         * Important!
         *   The core annotation functions can actually still work
         *   even if the video fails to load (thanks to our frame
         *   by frame processing).
         *   SO if the video doesn't load it is good to show that message
         *   but we don't want to "freeze" everything. :)
         */

        this.play_loading = false
        if (this.playPromise !== undefined) {
          this.playPromise.then(_ => {
            // Automatic playback started!
            // Show playing UI.
            //console.log("Success")

            this.playing = true
            this.playback_info = null // reset

            // Play should be before time update to reduce jerkiness
            // This is needed otherwise play trys to play based on actual time so it jerks back in time

            // example is  current frame guess is say 5, and if frame rate is 5, it's 5/5 = 1 time is 1
            this.primary_video.currentTime = this.video_current_frame_guess / this.current_video.frame_rate


            this.$emit('playing')
            this.primary_video.playbackRate = this.playback_rate

            this.video_animation_start()

          })
          .catch(error => {
            // Auto-play was prevented
            // Show paused UI.
            // console.log("Failed")

            // TODO treat 403 / permissions errors differently

            this.playback_info = "Please check your internet connection. Or try reloading. Contact us if this persists."
            this.$emit('video_play_failed')
            console.log(error)

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
     //  console.log("this.animation_request", this.animation_request)

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
      // console.log(this.primary_video.networkState)
      // integer codes for state...

      // must be at end?
      this.video_animation_start()
    },

	/**
		* @vue-event {Number} fr - Updates the ?frame=x query param in URL
		*/
    updateFrameUrl(frame) {
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
        console.log(error)
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
          //console.log("Used cache")
          this.preview_frame_url = this.preview_frame_url_dict[frame_number]
          this.preview_frame_refresh = Date.now()
          // may have been different issue but good to have something that changes if URL is the same

          return
        }
        else{
          if (this.preview_frame_loading) {
            //console.log("already loading")
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
            console.log(error)
            this.preview_frame_loading = false
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

      this.get_video_single_image_last_fired = new Date().getTime()

      this.video_current_frame_guess_update()
      const next_frames = this.get_next_n_frames(frame_number, 15)
      const prev_frames = this.get_previous_n_frames(frame_number, 15)
      const all_new_frames = [...new Set(next_frames.concat(prev_frames))];

      if (frame_number != this.prior_frame_number) {
        if(!this.frame_url_buffer[frame_number]){
          this.error = {}
          try{
            await this.add_new_frame_list_to_buffer(all_new_frames);
            const new_url = this.frame_url_buffer[frame_number]
            this.$emit('change_frame_from_video_event', new_url)
            this.go_to_keyframe_loading = false

            this.refresh = Date.now()
            this.$emit('set_canvas_dimensions')
            this.$emit('update_canvas');
            this.prior_frame_number = frame_number
          }
          catch(error){

            // Soft fail, ie can't get image and just want to annotate
            // of of video screen
            this.$emit('change_frame_from_video_event', false)
            console.log("Using video image instead of still frame.")
            //console.log(e)

            /* Context that on first load if it fails then need to "play" it to get first frame
             */
            if (this.first_play == true){
              this.muted = true   // required otherwise chrome won't auto play
              this.video_play()
            }

            this.go_to_keyframe_loading = false
            this.error = this.$route_api_errors(error)
          }
        }
        else{
          const new_url = this.frame_url_buffer[frame_number]
          this.$emit('change_frame_from_video_event', new_url)
          this.go_to_keyframe_loading = false
          this.refresh = Date.now()
          this.$emit('set_canvas_dimensions')
          this.$emit('update_canvas');
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
        }


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
          console.log(error)
          this.error = this.$route_api_errors(error)
        })
    },

    current_video_update: async function () {

      if (typeof this.current_video != "undefined") {

        this.first_play = true    // reset, 4k issue

        this.preview_frame_url_dict = {} // reset cache

        this.primary_video = document.getElementById("video_primary")

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
          const frame = parseInt(this.$route.query.frame || 0);
          await this.go_to_keyframe(frame);
          this.$refs.video_source_ref.src = this.current_video.file_signed_url
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

      if (this.task.id) {
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
          console.log(e) })
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
        }).catch(e => { console.log(e) })
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
          console.log(e)
          this.run_FAN_disabled = false
        })

    },

  }
}

) </script>
