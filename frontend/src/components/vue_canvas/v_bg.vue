<template>
</template>

<script lang="ts">

  import Vue from 'vue'

  export default Vue.extend({
    // to do rename this
    props: {
      "ord": {},
      "image": {
        default: null
      },
      "background": undefined,
      "current_file": {},
      "refresh": {
        default: Date.now()
      },
      "auto_scale_bg": {
        default: false
      },
      "canvas_filters": {
        default: () => ({
          brightness: 100,
          contrast: 100,
          grayscale: 0
        })
      },
      "annotations_loading": {
        default: true
      },
      "canvas_transform": {
        default: true
      },
      "canvas_element": {
        default: true
      }
    },

    methods: {
      draw_image_bg: function (ctx) {
        let local_brightness = this.canvas_filters['brightness']

        if (this.annotations_loading == true) {
          local_brightness -= 50
        }

        let brightness = `brightness(${local_brightness}%)`
        let contrast = `contrast(${this.canvas_filters['contrast']}%)`
        let grayscale = `grayscale(${this.canvas_filters['grayscale']}%)`
        ctx.filter = brightness + contrast + grayscale
        if (!this.$props.auto_scale_bg) {
          ctx.drawImage(
            this.image,
            0,
            0
          )

        } else {
          var hRatio = ctx.canvas.width / this.image.width;
          var vRatio = ctx.canvas.height / this.image.height;
          var ratio = Math.min(hRatio, vRatio);

          ctx.drawImage(
            this.image,
            0,
            0,
            ctx.canvas.width,
            ctx.canvas.height); // destination rectangle

        }
        ctx.filter = "none"
        // note, must be after we draw image if we want writing over top
        if (this.annotations_loading == true) {
          let font_size = 40
          ctx.fillStyle = "white";
          ctx.font = font_size + "px Verdana";

          if (this.current_file && this.current_file.image) {
            ctx.fillText("Loading",
              20,
              this.current_file.image.height / 2);
          }
        }
      },
      draw_color_bg: function (ctx) {
        let canvas = ctx.canvas;
        ctx.fillStyle = this.$props.background;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
      },
      draw: function (ctx, done) {
        // IMPORTANT this must be here
        // for refresh trigger to work.
        // we need to make a refresh update anytime we make
        // a change to image. (In annotation core)
        let local_refresh = this.refresh

        if (!this.$props.background) {
          this.draw_image_bg(ctx)

        } else {
          this.draw_color_bg(ctx)
        }


        done();

      }
    }
  })

</script>
