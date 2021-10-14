<template>
</template>

<script lang="ts">
  import Vue from 'vue'

  export default Vue.extend({
      props: {
        "ord" : {},
        "mouse_position": {},
        "height": {},
        "width": {},
        "x": {},
        "y": {},
        "show": {},
        "canvas_transform": {},
        "width_scaled": {},
        "height_scaled": {},
        "target_colour": {},
        "text_color": {},
        "canvas_element": {},
        "target_text": {},
        "target_type": '', // "canvas_cross" or "small_cross"
        "reticle_size": null,
        "label_settings": {
          default: null
        },
      },
      methods: {
        draw: function (ctx, done) {
          if(!this.$props.canvas_element){return}
          if (this.show == true) {
              //var canvas = ctx.canvas;
              if (this.width == 0) {
                done()
                return
              }

              var x = this.mouse_position.x;
              var y = this.mouse_position.y

              if (this.$props.target_colour != undefined) {
                ctx.strokeStyle = this.$props.target_colour.hex;
                let r = this.$props.target_colour.rgba.r
                let g = this.$props.target_colour.rgba.g
                let b = this.$props.target_colour.rgba.b
                ctx.fillStyle = "rgba(" + r + "," + g + "," + b + ", 1)";

                // redeclaring a scale here messes the other stuff up
                // would have to isolate if we wanted to do that
                //let font_size = "50"
                //ctx.font = font_size + "px Verdana";
              }
              if (this.$props.target_type === 'canvas_cross') {
                  if(x < 0 || y < 0){
                    done();
                    return
                  }
                  if(x >= this.$props.width || y >= this.$props.height){
                    done();
                    return
                  }

                  this.draw_text(ctx, x, y, this.$props.target_text, this.$props.text_color)
                  ctx.beginPath()
                  ctx.lineWidth = (1.5 / this.canvas_transform['canvas_scale_combined']).toString()
                  //ctx.strokeStyle = 'white',
                  // x and y are where the mouse is at
                  // top left of canvas is 0,0
                  // width and height is the bottom right edge

                  ctx.setLineDash([10, 5])
                  ctx.moveTo(x - 1, y)
                  ctx.lineTo(0, y)  // (end)

                  ctx.moveTo(x + 1, y)
                  ctx.lineTo(this.$props.width, y) // use original height here
                  // since if we use the canvas it will be off when scaled
                  // ie canvas.width is 320, which is correct,
                  // however this is absolute cordinates, so the mouse position
                  // adjusted for scale is 360, so therefore it doesn't draw the rest of the line

                  ctx.moveTo(x, y - 1) // line x, y start
                  ctx.lineTo(x, 0)  //  (end)

                  ctx.moveTo(x, y + 1) // line x, y start
                  ctx.lineTo(x, this.$props.height)

              }

              if (this.$props.target_type === 'small_cross') {
                ctx.beginPath()

                // If it's a high resolution image, then when we have a line of 1 it starts
                // to "shade" it so it still shows up, but poorly. (it makes it seem like we can't see it)
                // This dynamically scales it

                ctx.lineWidth = (1.5 / this.canvas_transform['canvas_scale_combined']).toString()
                //console.log(ctx.lineWidth)


                let line_length = this.$props.reticle_size / this.$props.canvas_transform['canvas_scale_combined']
                //console.log(line_length)
                ctx.setLineDash([]) // solid
                ctx.moveTo(x - 1, y)
                ctx.lineTo(x - line_length, y)  // x coordinate line to, y line to (end)

                ctx.moveTo(x + 1, y)
                ctx.lineTo(x + line_length, y)

                ctx.moveTo(x, y - 1) // line x, y start
                ctx.lineTo(x, y - line_length)  // x coordinate line to, y line to (end)

                ctx.moveTo(x, y + 1) // line x, y start
                ctx.lineTo(x, y + line_length)
              }

              ctx.stroke()


          }

          done();

        },
        draw_text: function (ctx, x, y, text, fill_color) {
          //let message = instance.label_file.label.name
          let message = ""

          if (text != undefined) {

            ctx.fillStyle = fill_color

            message += this.$props.target_text;

            ctx.fillText(message, x, y);
          }

        },

      }

    })


</script>
