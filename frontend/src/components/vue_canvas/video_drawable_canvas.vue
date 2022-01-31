<template>
  <div class="video_canvas" style="position: relative; height: 100%" >
    <div @click="$emit('on_click_details', current_frame)">
      <drawable_canvas
        :allow_zoom="allow_zoom"
        :image_bg="html_image"
        :canvas_height="canvas_height_computed"
        :canvas_width="canvas_width"
        :editable="editable"
        :auto_scale_bg="true"
        :refresh="refresh"
        :video_mode="true"
        :canvas_wrapper_id="canvas_wrapper_id || `canvas_wrapper__${file.id}`"
        :canvas_id="canvas_id || `canvas__${file.id}`"
        @refresh="refresh = Date.now()"
        ref="drawable_canvas"
      >
        <instance_list
          slot-scope="props"
          :instance_list="filtered_instance_list"
          :vertex_size="3"
          :refresh="refresh"
          :video_mode="true"
          :label_settings="label_settings"
          :show_annotations="true"
          :draw_mode="false"
          :canvas_transform="props.canvas_transform"
          slot="instance_drawer"
        >
        </instance_list>
      </drawable_canvas>

    </div>
    <v_video  v-if="is_mounted"
              @mouseover="hovered = true"
              :user_nav_width_for_frame_previews="false"
              :style="{maxWidth: this.$refs.drawable_canvas.canvas_width_scaled, position: 'absolute', bottom: '-95px', right: 0}"
              :player_width="canvas_width"
              :update_query_params="false"
              :player_height="`${video_player_height}px`"
              v-show="true"
              :class="`pb-0 ${hovered ? 'hovered': ''}`"
              :current_video="video"
              :video_mode="true"
              :video_primary_id="`video_primary__${file.id}`"
              @playing="video_playing = true"
              @pause="video_playing = false"
              @seeking_update="seeking_update($event)"
              :project_string_id="project_string_id"

              @go_to_keyframe_loading_started="set_keyframe_loading"
              @go_to_keyframe_loading_ended="change_frame_from_video"
              @video_animation_unit_of_work="video_animation_unit_of_work($event)"
              @video_current_frame_guess="current_frame = parseInt($event)"
              @slide_start="() => {}"
              @request_save="() => {}"
              @go_to_keyframe="() => {}"
              @set_canvas_dimensions="() => {}"
              @update_canvas="update_canvas"
              :current_video_file_id="file.id"
              :video_pause_request="video_pause"
              :video_play_request="video_play"
              :loading="any_loading"
              :view_only_mode="true"
              :has_changed="false"
              :canvas_width_scaled="$refs.drawable_canvas.canvas_width_scaled"
              ref="video_controllers"
              :show_video_nav_bar="show_video_nav_bar"
             >
    </v_video>
  </div>
</template>

<script>
import Vue from "vue";
import drawable_canvas from "./drawable_canvas";
import instance_list from "./instance_list";
import axios from "axios";
import {KeypointInstance} from "./instances/KeypointInstance";

  export default Vue.extend( {
    name: "video_drawable_canvas",
    components: {
      drawable_canvas,
      instance_list,
    },
    props: {
      canvas_wrapper_id:{
        default: undefined
      },
      project_string_id: {
        default: undefined
      },
      file: {
        default: null
      },
      editable:{
        default: true
      },
      auto_scale_bg:{
        default: false
      },
      text_color: {
        default: "#000000"
      },
      label_settings:{
        default: null
      },
      video:{
        default: undefined,
      },
      canvas_id: {
        default: undefined
      },
      canvas_height: {
        default: 800
      },
      canvas_width: {
        default: 800
      },
      initial_instances:{
        default: null
      },
      filtered_instance_by_model_runs:{
        default: null
      },
      allow_zoom:{
        default: true
      },
      show_video_nav_bar:{
        default: true
      },
      reticle_colour: {
        default: () => ({
          hex: '#ff0000',
          rgba: {
            r: 255,
            g: 0,
            b: 0,
            a: 1
          }
        })
      }
    },
    data: function(){
      return {
        loading: false,
        hovered: false,
        is_mounted: false,
        annotations_loading: false,
        get_instances_loading: false,
        refresh: new Date(),
        refresh_video_buffer: new Date(),
        html_image: new Image(),
        video_playing: false,
        go_to_keyframe_loading: false,
        video_play: null,
        video_pause: null,
        current_frame: 0,
        seeking: false,
        instance_frame_start: 0,
        video_player_height: 80,
        instance_buffer_size: 60,
        instance_buffer_dict: {},
        instance_buffer_error: {},
        instance_buffer_metadata: {},
        instance_list: [],

      }
    },
    beforeDestroy(){
      //console.debug("Destroyed")
      document.removeEventListener('focusin', this.focus_in)
      document.removeEventListener('focusout', this.focus_out)
    },
    watch: {
      instance_list: function(){
        this.$emit('update_instance_list', this.instance_list);
      },
      refresh_video_buffer: function(){
        this.get_video_instance_buffer()
      }
    },
    created() {
      document.addEventListener('focusin', this.focus_in)
      document.addEventListener('focusout', this.focus_out)
    },
    async mounted() {
      this.is_mounted = true;
      await this.$nextTick();
      await this.initialize_video();

    },
    methods:{
      set_keyframe_loading: function(value){
        this.go_to_keyframe_loading = value
      },
      initialize_video: async function(){
        this.$refs.video_controllers.reset_cache();
        await this.get_instances();
        await this.$nextTick();
        await this.$refs.video_controllers.current_video_update();
      },
      focus_in: function(){
        this.focused = true;
      },
      focus_out: function(){
        this.focused = false;
      },
      update_canvas: function(){
        this.$refs.drawable_canvas.update_canvas()
      },
      video_animation_unit_of_work: async function (image) {
        /*
         *  From animation in the context of getting
         *  passed an image from a video
         *  And NOT for pulling a single frame
         *
         *
         *  Refresh workaround note:
         *    As of Jan 16, 2020 it appears to not be
         *    since perhaps instance_list is changing?
         *
         *    Question, is "refresh" a heavy operation?
         *    the date thing shouldn't be, but not clear if the
         *    settimeout and/or it's relation to animation from does
         *    anthing?
         *
         */

        this.html_image = image;

        // //this.trigger_refresh_with_delay()
        // let index = this.current_frame - this.instance_frame_start
        // // todo getting buffer should be in Video component
        // // also this could be a lot smarter ie getting instances
        // // while still some buffer left etc.

        if (this.current_frame in this.instance_buffer_dict) {
          // We want to initialize the buffer dict before assinging the pointer on instance_list.
          this.initialize_instance_buffer_dict_frame(this.current_frame)
          // IMPORTANT  This is a POINTER not a new object. This is a critical assumption.
          // See https://docs.google.com/document/d/1KkpccWaCoiVWkiit8W_F5xlH0Ap_9j4hWduZteU4nxE/edit
          this.instance_list = this.instance_buffer_dict[this.current_frame];
        } else {
          this.video_pause = Date.now()

          this.get_instances(true)
        }
        this.$refs.drawable_canvas.canvas_wrapper.style.display = "";
        this.refresh = Date.now();
        this.update_canvas();
      },
      get_instances: async function (play_after_success=false) {
        if(this.get_instances_loading){ return }
        this.get_instances_loading = true;
        this.annotations_loading = true;

        await this.update_instance_list_from_buffer_or_get_new_buffer(play_after_success)
        this.get_instances_loading = false;
        this.update_canvas();

      },

      async get_video_instance_buffer(play_after_success) {
        /*
         * Directly triggers getting buffer
         * Caution, this should rarely be called directly
         * normally it's called in conjunction with something
         * that checks if we already have a local copy like
         *
         * Using project id from store for case of single file
         * permissions ie file/:file_id
         *
         */

        this.loading = true
        this.annotations_loading = true
        this.instance_buffer_error = {}

        this.instance_frame_start = this.current_frame
        if(!this.$props.project_string_id){
          return
        }
        let url = `/api/project/${this.$props.project_string_id}/video/${String(this.$props.file.id)}`

        url += `/instance/buffer/start/${this.current_frame}/end/${(this.current_frame + this.instance_buffer_size)}/list`
        try{
          const response = await axios.post(url, {
            directory_id : this.$store.state.project.current_directory.directory_id
          })
          // Get the buffer from the Server. Note that at this point it is not initialized.
          // We'll initialize class instances as per frame and not all at once for performance reasons.
          this.instance_buffer_dict = response.data.instance_buffer_dict
          this.instance_buffer_metadata = {};
          // Now set the current list from buffer
          if (this.instance_buffer_dict) {
            // We want to do the equals because that creates the reference on the instance list to buffer dict
            this.initialize_instance_buffer_dict_frame(this.current_frame)
            this.instance_list = this.instance_buffer_dict[this.current_frame]
          }
          else {
            // handle if buffer list doesn't load all the way?
            this.instance_list = []
          }

          this.loading = false
          this.annotations_loading = false
          setTimeout(() => this.refresh = Date.now(), 80)
          this.update_canvas();

          if (play_after_success == true) {
            this.video_play = Date.now()
          }
        }
        catch (error) {
          this.instance_buffer_error = this.$route_api_errors(error)
          console.debug(error);
          this.loading = false
        }
      },

      initialize_instance: function(instance){
        // TODO: add other instance types as they are migrated to classes.
        if(instance.type === 'keypoints' && !instance.initialized){
          let initialized_instance = new KeypointInstance(
            this.mouse_position,
            this.canvas_element_ctx,
            this.instance_context,
            this.trigger_instance_changed,
            this.instance_selected,
            this.instance_deselected,
            this.mouse_down_delta_event,
            this.mouse_position,
          );
          initialized_instance.populate_from_instance_obj(instance);
          return initialized_instance
        }
        else{
          return instance
        }
      },
      initialize_instance_buffer_dict_frame: function(frame_number){
        /**
         * This function initializes the instances of a frame's instance list.
         * We just do this once per frame, so this function should only be executed
         * one time per frame number. To control this we have the instance_buffer_metadata
         * to know which ones have been initialized.
         * TODO: Duplicated in annotation core. We need to find a way to reuse this in a semantically useful way.
         * */

        if(frame_number == undefined){ return }
        // We don't initialize again if we already initialized the frame.
        if(!this.instance_buffer_dict[frame_number]){ return }

        if(this.instance_buffer_metadata[frame_number] &&
          this.instance_buffer_metadata[frame_number].initialized){
          return
        }

        // Perform the instance_buffer_dict initialization.
        for(let i = 0; i < this.instance_buffer_dict[frame_number].length; i++){
          let current_instance = this.instance_buffer_dict[frame_number][i]
          current_instance = this.initialize_instance(current_instance);
          this.instance_buffer_dict[frame_number][i] = current_instance
        }

        // Set the metadata to prevent initializing again in the future
        if(this.instance_buffer_metadata[frame_number]){
          this.instance_buffer_metadata[frame_number].initialized = true;
        }
        else{
          this.instance_buffer_metadata[frame_number] = {initialized: true};
        }
      },
      async update_instance_list_from_buffer_or_get_new_buffer(play_after_success) {
        if (this.current_frame in this.instance_buffer_dict) {
          // Initialize instances to class objects before assigning pointer.
          this.initialize_instance_buffer_dict_frame(this.current_frame);
          // Instance list is always a pointer to the actual instance_buffer dict.
          // IMPORTANT  This is a POINTER not a new object. This is a critical assumption.
          // See https://docs.google.com/document/d/1KkpccWaCoiVWkiit8W_F5xlH0Ap_9j4hWduZteU4nxE/edit

          this.instance_list = this.instance_buffer_dict[this.current_frame];

          this.loading = false
          this.annotations_loading = false
          if(this.instance_buffer_metadata[this.current_frame] && this.instance_buffer_metadata[this.current_frame].pending_save){
            this.has_changed = true;
          }

        } else {
          await this.get_video_instance_buffer(play_after_success)
        }
        this.refresh = Date.now()
        this.update_canvas();
      },
      addImageProcess: function (src) {
        return new Promise((resolve, reject) => {
          let image = new Image()
          image.src = src
          if(process.env.NODE_ENV === 'testing'){
            image.crossOrigin = "anonymous";
          }
          image.onload = () => resolve(image)
          image.onerror = reject
        })
      },
      load_video_frame_from_url: function (url) {
        var self = this
        self.addImageProcess(url).then(image => {
          self.html_image = image
          if(self.$refs.drawable_canvas){
            self.$refs.drawable_canvas.canvas_wrapper.style.display = ""
            self.loading = false
            this.refresh = Date.now();
          }

        })
      },
      change_frame_from_video: function (url) {
        this.update_instance_list_from_buffer_or_get_new_buffer()
        if (url) {
          this.load_video_frame_from_url(url)
        }
      },

      seeking_update: function (seeking) {
        this.seeking = seeking
      },
    },
    computed:{
      filtered_instance_list: function(){
        const filtered_instance_id_list = this.$props.filtered_instance_by_model_runs.map(inst => inst.id)
        const new_instance_list = this.instance_list.filter(inst => filtered_instance_id_list.includes(inst.id));
        for(const inst of new_instance_list){
          const new_instance = this.$props.filtered_instance_by_model_runs.find(elm => elm.id === inst.id);
          inst.override_color = new_instance.override_color;
        }
        return new_instance_list;
      },
      any_loading() {
        return  this.annotations_loading || this.loading || this.get_instances_loading
      },
      style_max_width: function () {
        return "max-width:" + this.canvas_width_scaled + "px"
      },
      canvas_height_computed: function() {
        if (this.show_video_nav_bar) {
          return this.canvas_height - this.video_player_height
        }
        return this.canvas_height
      }
    }
  });
</script>

<style scoped>
  .hovered{
    opacity: 1;
  }
  .video_canvas:hover{
    cursor: pointer;
  }
</style>
