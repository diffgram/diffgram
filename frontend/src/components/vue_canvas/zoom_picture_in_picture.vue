
<template>
</template>

<script lang="ts">

  import Vue from 'vue'
  
  export default  Vue.extend({

      props: ["ord",
              "image",
              "mouse_position",
              "zoom_settings",
              "draw_mode"
        ],

      methods: {

        draw: function (ctx, done) {

          if (this.$store.state.annotation_state.draw == false) {
            if (this.draw_mode == true) {
              if (this.zoom_settings.on == true) {

                var x = this.mouse_position.x
                var y = this.mouse_position.y

                ctx.save()
                ctx.setTransform(1, 0, 0, 1, 0, 0)

                var ratio = this.zoom_settings.ratio
                var size = this.zoom_settings.size

                var draw_clip_x = x - (size / ratio);
                var draw_clip_y = y - (size / ratio);
                var draw_swidth = size // zoom in, 100 == normal, lower is more zoom
                var draw_sheight = size
                if (this.zoom_settings.location == "target_reticle") {
                  var draw_x = (x / ratio) - (size / ratio)
                  var draw_y = (y / ratio) - (size / ratio)
                } else {
                  var draw_x = 0
                  var draw_y = 0
                }
                var draw_width = size  // height of actual box
                var draw_height = size


                ctx.scale(ratio, ratio)

                ctx.drawImage(this.image,
                  draw_clip_x,
                  draw_clip_y,
                  draw_swidth,
                  draw_sheight,
                  draw_x,
                  draw_y,
                  draw_width,
                  draw_height);


                ctx.restore()
              }
            }
          }

          done();

        }
      }

    })


</script>
