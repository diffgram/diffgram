<script lang="ts">
import Vue from 'vue';

/**

 * @vue-data {string} top - Position of context menu from top of page
 * @vue-data {string} left - Position of context menu from left of page
*/


export default Vue.extend({
  name: 'frame_preview',
  props: {
    'frame_url' : {
      type: String, // string
      default: null,
    },
    'mouse_x': {
      type: Number,
      default: 500,
    },
    'mouse_y': {
      type: Number,
      default: 500,
    },
    'visible': {
      type: Boolean,
      default: false,
    },
    'width': {
      type: Number,
      default: 240,
    },
    'height': {
      type: Number,
      default: 180,
    },
    'refresh': {
      type: Number,
      default: null,
    },
    'frame_estimate': {
      type: Number,
      default: null,
    },
  },
  data() {

    return {
      error: false
    }
  },

  computed: {
    // values here in part a ratio / size of box? // eg 1/2
    mouse_x_px () {
      // Hide it case
      if (!this.visible || this.error) {return '-1000px'}
      // Show it case:
      return this.mouse_x + 50 + 'px'
    },
    mouse_y_px () {
      if (!this.visible || this.error) {return '-1000px'}
      return (this.mouse_y ) + 50 + 'px'
    },
    height_px () { return this.height +'px'},
    width_px () { return this.width +'px'}
   },

  watch: {
  },
  methods: {
    image_error: function (error){
      this.error = true
      console.error(error)
    }


  }
});
</script>
<template>
  <div
    class="frame-preview"
    :style="{bottom: mouse_y_px, left: mouse_x_px}"
  >
    <v-card
      :width="width"
      :height="height"
    >
    <img :style="{'max-height': height_px,
                   'max-width': width_px}"
          :src="$props.frame_url"
          width="100%"
          height="100%"
          @error="image_error($event)"
          @load="error=false"

          >
      <!-- This is just an estimate so not sure how we want to show this yet
           For now it's more just for debugging-->
      <!--
      {{frame_estimate}}
      -->
    </v-card>
  </div>
</template>
<style>
.frame-preview {
  position: absolute;
  margin: 0;
  z-index: 100;
}


</style>
