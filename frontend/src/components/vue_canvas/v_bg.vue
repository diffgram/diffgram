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
      },
      'canvas_height':{
        default: 0
      },
      'canvas_width':{
        default: 0
      },
      'degrees':{
        default: 0
      }
    },

    methods: {
      draw_image_bg: function (ctx) {
        if(!ctx.canvas){
          return
        }
        if(!this.image){
          return
        }
        let local_brightness = this.canvas_filters['brightness']

        let rotationDegrees = 0;
        let brightness = `brightness(${local_brightness}%)`
        let contrast = `contrast(${this.canvas_filters['contrast']}%)`
        let grayscale = `grayscale(${this.canvas_filters['grayscale']}%)`
        ctx.filter = brightness + contrast + grayscale

        let drawOptimizedImage = (image, degrees) => {
          var canvas = document.createElement('canvas');
          let ctx = canvas.getContext('2d')
          ctx.save()
          // ctx.clearRect(0, 0, canvas.width, canvas.height)

          if (degrees === 0) {
            ctx.drawImage(image, 0, 0)
          }
          else {
            canvas.width = this.canvas_width
            canvas.height = this.canvas_height
            ctx.translate(canvas.width / 2, canvas.height / 2)
            ctx.rotate(degrees * Math.PI / 180)

            if (Math.abs(degrees) === 180) {
              ctx.drawImage(image, -this.canvas_width / 2, -this.canvas_height / 2, this.canvas_width, this.canvas_height)
            }
            else { // 90 or 270 degrees (values for width and height are swapped for these rotation positions)
              ctx.drawImage(image, -this.canvas_width / 2, -this.canvas_height / 2, this.canvas_width, this.canvas_height)
            }
          }
          ctx.restore()

          return canvas
        }

        if (!this.$props.auto_scale_bg) {
          if(this.degrees != 0){
            let scaledImage = drawOptimizedImage(this.image, this.degrees)
            ctx.drawImage(
              scaledImage,
              0,
              0,
            )
          } else{
            ctx.drawImage(
              this.image,
              0,
              0,
            )
          }


        } else {
          let scale_x = ctx.canvas.width / this.image.width;
          let scale_y = ctx.canvas.height / this.image.height;
          let scaledImage = drawOptimizedImage(this.image, this.degrees)
          // ctx.clearRect(
          //   0,
          //   0,
          //   this.image.width,
          //   this.image.height
          // );
          ctx.resetTransform();
          ctx.drawImage(
            scaledImage,
            0,
            0,
            scaledImage.width,
            scaledImage.height,
            0,
            0,
            ctx.canvas.width,
            ctx.canvas.height); // destination rectangle
          ctx.scale(scale_x, scale_y)

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
