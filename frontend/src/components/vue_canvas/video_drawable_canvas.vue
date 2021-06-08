<template>
  <div>
      <drawable_canvas
        :image_bg="html_image"
        :canvas_height="canvas_height"
        :canvas_width="canvas_width"
        :editable="false"
        :auto_scale_bg="false"
        :refresh="refresh"
        :canvas_wrapper_id="`canvas_wrapper__${file.id}`"
        :canvas_id="`canvas__${file.id}`"
        ref="drawable_canvas"
      >
        <slot slot="instance_drawer"
              :ord="3"
              name="instance_drawer"
              :canvas_transform="$refs.drawable_canvas.canvas_transform">

        </slot>
      </drawable_canvas>

  </div>

</template>

<script>
import Vue from "vue";
import drawable_canvas from "./drawable_canvas";
import axios from "axios";
import {KeypointInstance} from "./instances/KeypointInstance";

  export default Vue.extend( {
    name: "video_drawable_canvas",
    components: {
      drawable_canvas,
    },
    props: {
      canvas_wrapper_id:{
        default: 'canvas_wrapper'
      },
      project_string_id: {
        default: undefined
      },
      file: {
        default: null
      },
      video_mode: {
        default: false
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
      video:{
        default: undefined,
      },
      canvas_id: {
        default: 'my_canvas'
      },
      canvas_height: {
        default: 800
      },
      canvas_width: {
        default: 800
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
        show_annotations: false,
        loading: false,
        annotations_loading: false,
        refresh: new Date(),
        html_image: new Image(),
        video_playing: false,
        current_frame: undefined,
        seeking: false,
        instance_frame_start: 0,
        instance_buffer_dict: {},
        instance_buffer_error: {},
        instance_buffer_metadata: {},
      }
    },
    methods:{
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

        this.show_annotations = false
        this.loading = true
        this.annotations_loading = true
        this.instance_buffer_error = {}

        this.instance_frame_start = this.current_frame

        let url = `/api/project/${this.$props.project_string_id}/video/${String(this.current_video_file_id)}`

        url += `/instance/buffer/start/${this.current_frame}
                /end/${(this.current_frame + this.label_settings.instance_buffer_size)}/list`
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

          this.show_annotations = true
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
            this.mouse_down_delta_event
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

          this.show_annotations = true
          this.loading = false
          this.annotations_loading = false
          if(this.instance_buffer_metadata[this.current_frame] && this.instance_buffer_metadata[this.current_frame].pending_save){
            this.has_changed = true;
          }

        } else {
          await this.get_video_instance_buffer(play_after_success)
        }
      },
      load_video_frame_from_url: function (url) {
        var self = this
        self.addImageProcess(url).then(image => {
          self.html_image = image
          self.canvas_wrapper.style.display = ""
          self.loading = false
          self.trigger_refresh_with_delay()
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
    }
  });
</script>

<style scoped>

</style>
