<template>
</template>
<script lang="ts">

  /*
  Draw current instance
  */

  import Vue from 'vue'
  import {cuboid} from './cuboid.js'

  Vue.prototype.$cuboid = new cuboid()

  export default Vue.extend({
    props: {
      "ord": {},
      "current_instance": {},
      "mouse_position": {},
      "canvas_transform": {},
      "draw_mode": {
        type: Boolean

      },
      "label_file_colour_map": {},
      "current_instance_template": {
        default: undefined
      },
      "instance_template_start_point": {
        default: undefined
      },
      "is_actively_drawing": {
        default: false
      },
      "instance_template_draw_started": {
        default: false
      }
    },
    data() {
      return {
        colour: null
      }
    },
    methods: {
      draw: function (ctx, done) {

        if (this.draw_mode == false) {
          done();
          return
        }


        if (this.is_actively_drawing == false) {
          done();
          return
        }
        if (!this.instance_template_draw_started) {
          done();
          return;
        }
        if (!this.$props.instance_template_start_point) {
          return
        }

        if(!this.$props.current_instance_template){
          return
        }

        let instance_template = this.$props.current_instance_template;

        let x_min = Math.min(this.$props.mouse_position.x, this.$props.instance_template_start_point.x)
        let y_min = Math.min(this.$props.mouse_position.y, this.$props.instance_template_start_point.y)
        let x_max = Math.max(this.$props.mouse_position.x, this.$props.instance_template_start_point.x)
        let y_max = Math.max(this.$props.mouse_position.y, this.$props.instance_template_start_point.y)
        ctx.textAlign = "start";
        ctx.lineWidth = '2'
        this.draw_instance_template_bounds(ctx, x_min, y_min);
        for (let instance of instance_template.instance_list) {
          // Just keypoints are supported for now
          if (instance.type == "keypoints") {
            instance.scale_width = Math.abs(this.$props.mouse_position.x - this.$props.instance_template_start_point.x)
            instance.scale_height = Math.abs(this.$props.instance_template_start_point.y - this.$props.mouse_position.y)
            instance.translate_x = x_min;
            instance.translate_y = y_min;
            instance.vertex_size = 2;
            instance.line_width = 2;
            instance.draw(ctx);
          }
        }
        done();

      },
      draw_instance_template_bounds: function (ctx, x_min, y_min) {
        ctx.fillStyle = "rgba(228, 230, 232, 0.5)";

        ctx.fillRect(x_min,
          y_min,
          Math.abs(this.$props.mouse_position.x - this.$props.instance_template_start_point.x),
          Math.abs(this.$props.mouse_position.y - this.$props.instance_template_start_point.y))
        ctx.fill();


      },
      set_color: function (instance, ctx, opacity) {
        this.colour = this.label_file_colour_map[instance.label_file.id]

        if (this.colour != undefined) {
          ctx.strokeStyle = this.colour.hex
          let r = this.colour.rgba.r
          let g = this.colour.rgba.g
          let b = this.colour.rgba.b
          ctx.fillStyle = "rgba(" + r + "," + g + "," + b + "," + opacity + ")";
        }
      },

    }

  })


</script>
