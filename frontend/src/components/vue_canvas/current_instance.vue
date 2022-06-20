<template>
</template>
<script lang="ts">

  /*
  Draw current instance
  */

  import Vue from 'vue'
  import { cuboid } from './cuboid.js'
  Vue.prototype.$cuboid = new cuboid()

export default Vue.extend({
      props: {
        "ord": {},
        "current_instance": {},
        "mouse_position": {},
        "canvas_transform": {},
        "draw_mode" : {
            type: Boolean

        },
        "render_mode": {
          default: null
        },
        "label_file_colour_map": {},
        "is_actively_drawing": {
          default: false
        },
        "zoom_value": {
          type: Number,
          default: 1
        }
      },
      data () {
        return {
          colour: null
        }
      },
      methods: {
        draw: function (ctx, done) {

          function toInt(n) { return Math.round(Number(n)); };

          if (this.draw_mode == false) {
            done();
            return
          }

          if (this.is_actively_drawing == false) {
            done();
            return
          }

          let instance = this.current_instance

          if (!instance.label_file) {
            done();
            return
          }

          if (instance == undefined) {
            done();
            return
          }

          ctx.beginPath()

          ctx.textAlign = "start";
          ctx.lineWidth = '2'

          if (instance.type == "cuboid") {
            this.draw_cuboid(instance, ctx)
          }
          else if (instance.type == "ellipse") {
            this.draw_ellipse(instance, ctx)
          }
          else if (instance.type == "curve") {
            this.draw_cuadratic_curve(instance, ctx)
          }

          else if (instance.type == "box") {
            this.draw_box(instance, ctx)
          }

          else if (["polygon", "line"].includes(instance.type)) {
            this.draw_polygon(instance, ctx)
          }

          done();

        },

        set_color: function (instance, ctx, opacity){
          this.colour = this.label_file_colour_map[instance.label_file.id]

          if (this.colour != undefined) {
            ctx.strokeStyle = this.colour.hex
            let r = this.colour.rgba.r
            let g = this.colour.rgba.g
            let b = this.colour.rgba.b
            ctx.fillStyle = "rgba(" + r + "," + g + "," + b + "," + opacity + ")";
          }
        },

        draw_cuadratic_curve: function(instance, ctx){
          if(instance.points.length === 0){
            return
          }
          ctx.beginPath();
          this.set_color(instance, ctx, 1);
          ctx.moveTo(instance.p1.x, instance.p1.y)
          const midpoint = {x: (this.mouse_position.x + instance.p1.x) / 2, y: (this.mouse_position.y + instance.p1.y) / 2}
          ctx.quadraticCurveTo(midpoint.x, midpoint.y , this.mouse_position.x, this.mouse_position.y);


          ctx.stroke();
        },

        draw_cuboid: function (instance, ctx) {
          /* instance, current instance object
           * ctx
           *
           * draws the front and back cuboid faces,
           * then draws the 4 side lines
           *
           * Keeping this seperate from cuboid.js for now,
           * since the "new" instance and the instance list will likely be different.
           * Maybe once better handle move in to cuboid.js
           */
          // TODO pass specifics to draw face...
          if(instance.cuboid_current_drawing_face === 'first'){
            this.$cuboid.draw_cuboid_face(instance.rear_face, ctx)
          }
          else if(instance.cuboid_current_drawing_face === 'second'){
            this.set_color(instance, ctx, 0.4);
            this.$cuboid.draw_cuboid_face(instance.rear_face, ctx, true)
            this.$cuboid.draw_cuboid_face(instance.front_face, ctx)
            this.set_color(instance, ctx, 0);
            this.$cuboid.draw_cuboid_sides( instance.front_face,
              instance.rear_face,
              ctx)

          }
          ctx.stroke();



        },

        draw_ellipse: function (instance, ctx) {

          // TODO clarify why this condition is only for box
          // (It is needed but, NOT for polygons)
          if (this.$store.state.annotation_state.draw != true) {
            return
          }

          ctx.fillStyle = this.$get_sequence_color(instance.sequence_id)
          ctx.fillText(instance.label_file.label.name, instance.x_min, instance.y_min);

          this.set_color(instance, ctx, 1)

          ctx.setLineDash([0])

          ctx.ellipse(
            instance.center_x,
            instance.center_y,
            instance.width,
            instance.height,
            0,
            0,
            2 * Math.PI)

          ctx.stroke()
        },
        draw_box: function (instance, ctx) {

          // TODO clarify why this condition is only for box
          // (It is needed but, NOT for polygons)
          if (this.$store.state.annotation_state.draw != true) {
            return
          }

          ctx.fillStyle = this.$get_sequence_color(instance.sequence_id)
          ctx.fillText(instance.label_file.label.name, instance.x_min, instance.y_min);

          // this is done via target reticle now
          /*
          if (instance.number != undefined) {
            ctx.fillText(instance.number, instance.x_max, instance.y_min)
          }
          */

          this.set_color(instance, ctx, 1)

          ctx.setLineDash([0])
          ctx.rect(instance.x_min,
            instance.y_min,
            instance.width,
            instance.height)

          ctx.stroke()
        },

        draw_polygon: function (instance, ctx) {
          /* We use this for polygon and line because
           * the line we want to show the points while drawing
           *
           *  TODO this should be more similar to logic in instance_list.vue
           *  (There are some differences so yes it can't be identical but still)
           *
           * */

          let points = instance.points
          let circle_size = 4 / this.$props.zoom_value

          this.set_color(instance, ctx, 1)

          // If there is at least 1 point, draw the first point
          if (points.length >= 1) {
            if (typeof this.colour != "undefined") {

              if (instance.number != undefined) {
                ctx.fillText(instance.number, points[0].x, points[0].y)
              }
              ctx.fillText(instance.label_file.label.name, points[0].x, points[0].y)

              this.set_color(instance, ctx, .5)

              ctx.moveTo(points[0].x, points[0].y)

              // TODO curious about differentiating first point
              // ie different colour? tried size but didn't quite look right.

              ctx.arc(points[0].x, points[0].y, circle_size, 0, 2 * Math.PI);
            }
          }

          // If there is at least 2 points, draw the rest
          if (points.length >= 2) {
            for (var i = 0; i < points.length - 1; i++) {
              ctx.arc(points[i].x, points[i].y, circle_size, 0, 2 * Math.PI);
              ctx.lineTo(points[i + 1].x, points[i + 1].y)
            }
            ctx.arc(points[points.length - 1].x,
              points[points.length - 1].y, circle_size, 0, 2 * Math.PI);
          }

          // If there is at least 1 point, after drawing first stuff
          // also draw line to show user where next point would land
          if (points.length >= 1) {
            ctx.lineTo(this.mouse_position.x, this.mouse_position.y)
          }

          if (instance.type == "line") {
            ctx.lineWidth *= 2
          }

          if (instance.type == "polygon") {
            ctx.closePath()
            ctx.stroke()
            ctx.fill()
          } else {
            ctx.stroke()
          }

        }

      }

    })


 </script>
