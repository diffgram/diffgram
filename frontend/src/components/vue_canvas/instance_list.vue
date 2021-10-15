<template>
</template>
<script lang="ts">

  /*
  Draw existing instances
  */

  import Vue from 'vue'
  import { cuboid } from './cuboid.js'
  import { ellipse } from './ellipse.js'
  Vue.prototype.$cuboid = new cuboid()
  Vue.prototype.$ellipse = new ellipse()


 export default Vue.extend({
      props: {
        "ord": {},
        "mode": {
          default: 'default'
        },
        "instance_list": {},
        "issues_list": undefined,
        "width": undefined,
        "height": undefined,
        "compare_to_instance_list_set": {
          default: null
        },
        "auto_border_polygon_p1": undefined,
        "auto_border_polygon_p2": undefined,
        "is_actively_resizing": {
          "default": false,
          type: Boolean
        },
        "current_frame": undefined,
        "is_actively_drawing": undefined,
        "video_mode": undefined,
        "current_instance": {},
        "vertex_size": {
          default: 0,
          type: Number
        },
        "refresh": {},
        "mouse_position" : {},
        "draw_mode": {
          default: true
        },
        "canvas_transform" : {},
        "show_annotations": {},
        "annotations_loading": {},
        "label_file_colour_map": {},
        "label_settings": {
          default: null
        },
        "instance_focused_index": {
          default: null
        },
        // CAUTION  there is some type of performance issue with monitoring cuboid_hover_index
        // when we are also emiting an event
        "hidden_label_id_list": {
          default: () => []
        },
        "emit_instance_hover": {
          type: Boolean,
          default: true
          // if True will run checks for hover, otherwise false to save computation
        },
        "default_instance_opacity":{
          type: Number,
          default: 0.25
        }
      },

      /* ord, order of drawing on canvas
       * instance_list, list of instance objects (dictionaries),
       * current_box, dictionary,
       * refresh, integer / hack for forcing reactive property change
       * mouse_position, dictionary, x, y
       * draw_mode, boolean
       * canvas_transform, dictionary,
       * show_annotations, boolean
       * */
      data() {
        return {
          colour: null,
          circle_size: null,
          hovered_figure_id: null,

          count_instance_in_ctx_paths: 0,
          cuboid_hovered_face: undefined,
          prev_cuboid_hovered_face: undefined,
          count_issues_in_ctx_paths: 0,

          instance_hover_index: -1,
          issue_hover_index: -1,
          previous_instance_hover_index: -2,
          previous_issue_hover_index: -2,

          instance_hover_type: null,

          instance_rotate_control_mouse_hover: null

        }
      },

      methods: {

        toInt: function (n) {
          return Math.round(Number(n));   // TODO review if can use built in instead
        },
        get_instance_corner: function (instance){
          if(instance.type === 'polygon'){
            return {x: instance.points[0].x +10, y: instance.points[0].y + 10}
          }
          else if(instance.type === 'box'){
            return {x: instance.x_max +10, y: instance.y_min + 20};
          }
          else if(instance.type === 'point'){
            return {x: instance.points[0].x +10 , y: instance.points[0].y + 10}
          }
          else if(instance.type === 'line'){
            return {x: instance.points[0].x +10, y: instance.points[0].y + 10}
          }
          else if(instance.type === 'ellipse'){
            this.$ellipse.generate_ellipse_corners(instance, instance.width, instance.height)
            return {x: instance.corners.top_right.x +10, y: instance.corners.top_right.y + 10}
          }
          else if(instance.type === 'curve'){
            return {x: instance.cp.x +10, y: instance.cp.y + 10}
          }
          else if(instance.type === 'cuboid'){
            return {x: instance.front_face.top_right.x +10, y: instance.front_face.top_right.y + 10}
          }
          else if(instance.type === 'keypoints'){
            return {x: Math.max(...instance.nodes.map(n => n.x)), y: Math.min(...instance.nodes.map(n => n.y))}
          }
          else{
            return undefined
          }
        },
        isInText(ctx, region, x, y) {
          // source:
          //https://stackoverflow.com/questions/28706989/how-do-i-check-if-a-mouse-click-is-inside-a-rotated-text-on-the-html5-canvas-in

          ctx.beginPath();
          ctx.rect(region.x, region.y, region.w, region.h);

          return ctx.isPointInPath(x, y);
        },

        is_mouse_in_path_issue: function (ctx, region, i, issue) {

          // This is first because we always want user to know which one they are on
          if (this.isInText(
            ctx,
            region,
            this.mouse_position.raw.x,
            this.mouse_position.raw.y)) {
            if (this.issue_hover_index != i){
              this.issue_hover_index = i

            }
            this.count_issues_in_ctx_paths += 1;
          }

        },
        draw_alert_icon: function(ctx, x, y, i, issue){
          if(!ctx.material_icons_loaded){
            return
          }
          const old_color = ctx.fillStyle;
          const old_font = ctx.font
          ctx.font = '24px material-icons';
          ctx.fillStyle = 'rgb(255,175,0)';
          const text_icon = 'error';
          const text = ctx.fillText(text_icon, this.toInt(x -20), this.toInt(y + 20));
          ctx.fillStyle = old_color;
          ctx.font = old_font;
          const measures = ctx.measureText(text_icon);
          // Create an invisible box for click events.
          const region = {x: x - 24 , y: y - 24 , w: measures.width, h: 100};
          this.is_mouse_in_path_issue(ctx, region, i, issue)
        },
        draw_issues_markers(ctx){
          if(!this.$props.issues_list || this.$props.issues_list.length === 0){
            return
          }
          this.$props.issues_list.forEach((issue, i) =>{
            if(issue.status === 'closed'){return}
            if(this.$props.video_mode && issue.marker_frame_number != this.$props.current_frame){
              return
            }

            if(issue.marker_type === 'point' && issue.marker_data && issue.marker_data.x && issue.marker_data.y){
              this.draw_alert_icon(ctx, issue.marker_data.x, issue.marker_data.y, i, issue);

            }

          })

        },
        draw_pause: function(instance, ctx){
          if(!ctx.material_icons_loaded){
            return
          }
          const old_color = ctx.fillStyle;
          const old_font = ctx.font
          ctx.font = '30px material-icons';
          ctx.fillStyle = 'rgb(0,0,0)';
          const point = this.get_instance_corner(instance)
          ctx.fillText('pause', point.x, point.y);
          ctx.fillStyle = old_color;
          ctx.font = old_font;
        },
        draw_checkmark: function(instance, ctx){
          if(!ctx.material_icons_loaded){
            return
          }
          const old_color = ctx.fillStyle;
          const old_font = ctx.font
          ctx.font = '50px material-icons';
          ctx.fillStyle = 'rgb(76,175,80)';
          const point = this.get_instance_corner(instance)
          ctx.fillText('check_mark', point.x, point.y);
          ctx.fillStyle = old_color;
          ctx.font = old_font;
        },
        draw_circle: function (x, y, ctx) {
          /* March 31, 2020
           *  In prior context we were calling this beside the regular line
           * We are now trying to split that apart, and in this new context it
           * may not be needed to do this reset with move to.
           *
           * Straight removing causes some artifacts so leaving it for now
           */
          ctx.arc(x, y, this.$props.vertex_size, 0, 2 * Math.PI);
          ctx.moveTo(x, y) // reset
        },

        draw_circle_from_instance: function (instance, points, index, ctx) {

          let x = points[index].x
          let y = points[index].y

          this.draw_circle(x, y, ctx)


          if(points[index].hovered_while_drawing || instance.type === 'line'){
            ctx.fill();
            ctx.stroke();
          }
          else{
            ctx.fill();
            ctx.stroke();
          }


        },

        // MAIN function
        draw: function (ctx, done) {

          if (this.show_annotations != true) {
            done()
            return
          }
          this.circle_size = 6 / this.canvas_transform['canvas_scale_combined']
          let font_size = this.label_settings.font_size / this.canvas_transform['canvas_scale_combined']
          ctx.font = font_size + "px Verdana";

          this.count_issues_in_ctx_paths = 0   // reset
          this.count_instance_in_ctx_paths = 0   // reset


          // MAIN loop
          for (var i in this.instance_list) {
            this.draw_single_instance(ctx, i)
          }

          this.draw_issues_markers(ctx);

          this.check_null_hover_case()    // careful, these should fire outside of main loop

          this.emit_unified_hover_event()

          done();

        },


        draw_single_instance_limits: function (instance, i) {

          if (instance.type == 'tag') { // tag is whole image so nothing to draw.
            return false
          }
          if(instance.hidden){
            return false
          }

          if (instance.soft_delete == true &&
            this.label_settings.show_removed_instances != true) {
            return false
          }
          // ie on first load from database .selected is undefined
          if (instance.label_file == undefined) {
            return false
          }
          if (this.instance_focused_index != undefined) {
            if (this.instance_focused_index != i) {
              return false
            }
          }
          /* More work then storing the 'visible' state, but in the context
           * of video this feels like stronger solution.
           * Also argue that if it does find something it returns so it 'saves'
           * the work of rendering, ie end result is probably less or equal work.
           */
          if (this.hidden_label_id_list.includes(instance.label_file_id) ) {
            return false
          }
          // not quite right place, but need to handle returning if false
          // This assumes we can get it from the 'master' list
          // eg if the label template color is changed... etc.

          if(this.label_file_colour_map){
            this.colour = this.label_file_colour_map[instance.label_file_id]
          }

          if (this.colour == undefined) {
            // Context is for Tasks, where we may have tasks that have instances that
            // aren't present in Label Template (label_file_colour_map)
            // at the moment this is less preferred because it's harder to update
            // and requires storing more data per instance (vs just referencing a map)
            if (instance.label_file &&
                instance.label_file.colour) {
              this.colour = instance.label_file.colour
            } else {
              // default fallback, just set it to black if
              // defined color is not available
              // otherwise risks not rendering it (which is prob worse)
              this.colour = {}
              this.colour.rgba = {
                r: 255,
                g: 255,
                b: 255
                }
            }
          }

          return true
        },

        color_instance: function (instance, ctx) {
          // TODO test this better, and also try to move other colors stuff here...

          let strokeColor = undefined;
          let fillColor = undefined;
          let lineWidth = undefined;

          if (instance.fan_made == true) {
            ctx.setLineDash([3])
          } else {
            ctx.setLineDash([0])
          }
          if(this.instance_select_for_issue){
            // Case of selecting instance for issue creation
            let r = 255
            let g = 255
            let b = 255
            fillColor = "rgba(" + r + "," + g + "," + b + ", 1)";
          }

          // Determine FILL COLOR
          if (instance.change_type != undefined) {
            if (instance.change_type == "added") {
              fillColor = "rgba(" + 0 + "," + 255 + "," + 0 + `, ${this.$props.default_instance_opacity})`;
            }
            else if (instance.change_type == "unchanged") {
              fillColor = "rgba(" + 255 + "," + 255 + "," + 255 + `, ${this.$props.default_instance_opacity})`;
            }
            else if (instance.change_type == "deleted") {
              fillColor = "rgba(" + 255 + "," + 0 + "," + 0 + `, ${this.$props.default_instance_opacity})`;
            }
          }
          else {

            let r = 255
            let g = 255
            let b = 255

            // TODO can we move this somewhere else, ie as part of each component?
            if(this.colour.rgba){
              r = this.colour.rgba.r
              g = this.colour.rgba.g
              b = this.colour.rgba.b
            }
            else if (instance.label_file && instance.label_file.colour && instance.label_file.colour.rgba) {
              // Fallback: the internal instance color instead of colour map if available.
              r = instance.label_file.colour.rgba.r
              g = instance.label_file.colour.rgba.g
              b = instance.label_file.colour.rgba.b
            }
            fillColor = "rgba(" + r + "," + g + "," + b + `, ${this.$props.default_instance_opacity})`;
          }

          // Determine STROKE COLOR
          if (instance.change_type != undefined) {
            if (instance.change_type == "added") {
              strokeColor = "green";
            }
            else if (instance.change_type == "unchanged") {
              strokeColor = "white";
            }
            else if (instance.change_type == "deleted") {
              strokeColor = "red";
            }
          } else {

            // good to have defaults here
            // in case something wacky with if (exists) logic

            if (this.mode == 'gold_standard') {
              strokeColor = "#FFD700"
            }
            if (this.mode == 'default') {
              if(this.colour){
                strokeColor = this.colour.hex
              }
              else if(instance.label_file && instance.label_file.colour && instance.label_file.colour.rgba){
                // Fallback for when this.colour is not available
                strokeColor = instance.label_file.colour.hex;
              }
              if(this.$props.default_instance_opacity === 1){
                strokeColor = "#FFFFFF"
              }

            }
            if(instance.override_color && !instance.selected){
              fillColor = "rgba(" + 255 + "," + 255 + "," + 255 + ", .25)";
              strokeColor = instance.override_color;
              ctx.setLineDash([[5]])
              ctx.strokeStyle = strokeColor;
              ctx.fillStyle = fillColor;
              ctx.lineWidth = 1;
            }
            lineWidth = '2'
            if (instance.selected == true) {
              strokeColor = "blue"
            }
            if(this.instance_select_for_issue && !this.view_issue_mode){
              if(instance.selected){
                strokeColor = "green"
                lineWidth = '4';
                this.draw_checkmark(instance, ctx);
              }
            }
            else if(this.view_issue_mode){
              if(instance.selected){
                strokeColor = "green"
                lineWidth = '4';
                if(this.instance_select_for_issue){
                  this.draw_checkmark(instance, ctx);
                }
              }
            }
          }

          ctx.strokeStyle = strokeColor;
          ctx.fillStyle = fillColor;
          ctx.lineWidth = lineWidth;

          return {
            strokeColor: strokeColor,
            fillColor: fillColor,
            lineWidth: lineWidth
          }
        },

        draw_single_instance: function (ctx, i) {
          var instance = this.instance_list[i]

          let result = this.draw_single_instance_limits(instance, i)

          if (result == false)  {
            return
          }

          // note this is a convience function for toher things that test falsyness
          // may nto need it, but that's why it's here and not in limits
          // (glancing at it looks like it's a return thing but it's not.)
          if (instance.selected == undefined){
            instance.selected = false
          }
          // TODO review this.colour isolation here


          ctx.textAlign = "start";
          // WIP , restrict movement to center point only
          //draw_circle(instance, instance.x_min + instance.width/2, instance.y_min + instance.height/2, ctx)



          const color_data = this.color_instance(instance, ctx)

          // TODO abstract to function ie for use with other "screen
          // rendered types" like polygon
          if (instance.rating) {
            for (let rating_index = 0; rating_index < instance.rating; rating_index++) {
              let x = instance.x_min + (rating_index * 35)
              this.drawStar(x, instance.y_max + 3, 5, 12, 6, ctx);
            }
          }
          if (instance.type == "box") {
            ctx.beginPath()

            this.draw_box(instance, ctx, i)
            ctx.lineWidth = this.get_spatial_line_size()
            ctx.stroke()
          }

          else if (["polygon", "line"].includes(instance.type)) {
            ctx.beginPath()
            this.draw_polygon(instance, ctx, i)
          }

          else if (instance.type == "cuboid") {
            ctx.beginPath()
            ctx.lineWidth = this.get_spatial_line_size()
            let cuboid_result = this.draw_cuboid(instance, ctx, i)
            ctx.stroke()
          }

          else if (instance.type == "ellipse") {
            ctx.beginPath()
            let cuboid_result = this.draw_ellipse(instance, ctx, i)
            ctx.lineWidth = this.get_spatial_line_size()
            ctx.stroke()
          }
          else if(instance.type === 'curve'){
            ctx.beginPath()
            ctx.lineWidth = this.get_spatial_line_size()
            this.draw_cuadratic_curve(instance, ctx, i);
            ctx.stroke()
          }
          else if (instance.type == "point") {
            ctx.beginPath()
            this.draw_point(instance, ctx, i)
            ctx.lineWidth = '2'
            ctx.stroke()
          }
          else if (instance.type == "keypoints") {
            instance.strokeColor = color_data.strokeColor;
            instance.lineWidth = this.get_spatial_line_size();
            instance.vertex_size = this.$props.vertex_size;
            instance.draw(ctx);
            if(instance.is_hovered){
              this.instance_hover_index = i
              this.count_instance_in_ctx_paths +=1;
              this.instance_hover_type = instance.type;
            }
            const radius = (this.$props.vertex_size) / this.canvas_transform['canvas_scale_combined']

            this.instance_rotate_control_mouse_hover = instance.draw_rotate_point(
              ctx,
              this.is_mouse_in_path,
              radius
            )

            if (this.instance_rotate_control_mouse_hover == true){
              this.instance_hover_index = i   // becuase rotate point may not be in instance
              this.count_instance_in_ctx_paths +=1;
              this.instance_hover_type = instance.type
            }

          }

          // TODO we may want to add the edit circle things
          // (right now the stroke goes over the fill and it looks funny)

          // TODO maybe could be a fancier highlight method
          // ie maybe rect plus shaded or something
          // ie https://stackoverflow.com/questions/10487882/html5-change-opacity-of-a-draw-rectangle
          ctx.stroke()
          // Reset line width after drawing.
          ctx.lineWidth = '2'
            /*
            if (this.instance_focused_index != undefined) {
              if (instance.id === this.instance_focused_index) {
                ctx.strokeStyle = "blue"
              }
            }
            */

           this.draw_icons(instance, ctx)

        },

        draw_icons: function (instance, ctx) {
          if(instance.pause_object == true){
            this.draw_pause(instance, ctx);
          }
        },

        get_spatial_line_size: function (){
          return this.$props.label_settings.spatial_line_size / this.canvas_transform['canvas_scale_combined']
        },

        // edit circles
        draw_many_polygon_circles: function (instance, i, ctx) {

          // note different stopping point from lines
          const fillStyle = ctx.fillStyle;
          const strokeStyle = ctx.strokeStyle

          for (var j = 0; j < instance.points.length; j++) {
            ctx.beginPath();
            ctx.fillStyle = '#ffffff';
            ctx.strokeStyle = '#bdbdbd';
            if (instance.points[j].hovered_while_drawing){
              ctx.fillStyle = 'white';
              ctx.strokeStyle = 'white';
            }
            if(instance.points[j].point_set_as_auto_border){
              ctx.fillStyle = '#4caf50';
              ctx.strokeStyle = '#4caf50';
            }
            this.draw_circle_from_instance(instance, instance.points, j, ctx)
            ctx.fillStyle = fillStyle;
            ctx.strokeStyle = strokeStyle;
            this.is_mouse_in_path(ctx, i, instance)
          }
          ctx.fillStyle = fillStyle;
          ctx.strokeStyle = strokeStyle;
        },

        draw_polygon_lines: function (instance, ctx, points) {

          // All lines after first
          // excluding last line
          // because the last line "loops" back to the first element

          for (var j = 0; j < points.length - 1; j++) {
            // for example if points.length is 11, we do
            // up to j = 9 so j + 1 = 10 which is last index
            ctx.lineTo(points[j + 1].x, points[j + 1].y)
          }

        },

        is_mouse_in_path: function (ctx, i, instance, figure_id = undefined) {
          if(!this.mouse_position){
            return false
          }
          // This is first because we always want user to know which one they are on
          if (ctx.isPointInPath(
            this.mouse_position.raw.x,
            this.mouse_position.raw.y)) {

            if (this.instance_hover_index != i){
              this.instance_hover_index = i
              this.instance_hover_type = instance.type
              this.hovered_figure_id = figure_id;
            }
            this.count_instance_in_ctx_paths += 1
            return true;
          }
          return false

        },

        emit_unified_hover_event: function () {
          /*
           * we only want to emit 1 event in case timing issue with this stuff
           * otherwise potential timing issues, ie bouncing back and forth
           * and seems easier to just take "last" one it found in path.
           *
           * We had a check on both the path and null case to update,
           * but now that we have this unified thing, also need to see if we emit the
           * event at all. otherwise we are always emiting even if no changes
           */

          if (this.emit_instance_hover == true) {

            if (this.instance_hover_index != this.previous_instance_hover_index) {

              this.previous_instance_hover_index = this.instance_hover_index

              this.$emit('instance_hover_update',
                [this.instance_hover_index,
                 this.instance_hover_type,
                 this.hovered_figure_id,
                 this.instance_rotate_control_mouse_hover])
            }
            if(this.instance_hover_type === 'cuboid' && this.prev_cuboid_hovered_face != this.cuboid_hovered_face){
              this.prev_cuboid_hovered_face = this.cuboid_hovered_face;
              this.$emit('cuboid_face_hover_update', this.cuboid_hovered_face)
            }


            if (this.issue_hover_index != this.previous_issue_hover_index) {

              this.previous_issue_hover_index = this.issue_hover_index

              this.$emit('issue_hover_update', this.issue_hover_index)
            }
          }
        },

        check_null_hover_case: function () {

          if (this.count_instance_in_ctx_paths == 0) {

            if (this.instance_hover_index != null) { // only update on change
              this.instance_hover_index = null   // careful need to reset this here too
              this.instance_hover_type = null
              this.hovered_figure_id = null   // reset
            }
          }
          // Do the same for issues.
          if (this.count_issues_in_ctx_paths === 0) {

            if (this.issue_hover_index != null) {
              this.issue_hover_index = null
            }
          }
        },
        generate_polygon_mid_points(instance, ctx, i, points, figure_id = undefined){
          const midpoints_polygon = []
          for(let i = 1; i < points.length; i++){
            const prev = points[i - 1];
            const current = points[i];
            midpoints_polygon.push({
              x: (prev.x + current.x) / 2,
              y: (prev.y + current.y) / 2,
              figure_id: figure_id
            })
          }
          midpoints_polygon.push({
            x: (points[0].x + points[points.length - 1].x) / 2,
            y: (points[0].y + points[points.length - 1].y) / 2
          })
          if(figure_id){
            if(!instance.midpoints_polygon){
              instance.midpoints_polygon = {
                [figure_id]: midpoints_polygon
              }
            }
            else{
              instance.midpoints_polygon[figure_id] = midpoints_polygon
            }

          }
          else{
            instance.midpoints_polygon = midpoints_polygon;
          }

        },
        draw_polygon_midpoints(instance, ctx, i, figure_id = undefined){
          let midpoints_polygon = instance.midpoints_polygon
          if(figure_id){
            midpoints_polygon = instance.midpoints_polygon[figure_id]
          }
          if(instance.midpoint_hover == undefined){return}
          // Only draw when hovered in
          const point = midpoints_polygon[instance.midpoint_hover];
          if(point == undefined){return}
          const radius = (this.$props.vertex_size) / this.canvas_transform['canvas_scale_combined']
          this.draw_single_path_circle(point.x, point.y, radius, ctx);

        },

        draw_polygon: function (instance, ctx, i) {
          let result = this.draw_polygon_main_section(instance, ctx, i)
                       this.draw_polygon_control_points(instance, ctx, i)
        },
        draw_polygon_figure: function(instance, ctx, i, points, figure_id = undefined){
          if(instance.type === 'polygon' && instance.selected){
            this.generate_polygon_mid_points(instance, ctx, i, points, figure_id)
            this.draw_polygon_midpoints(instance, ctx, i, figure_id)
          }
          ctx.beginPath();
          const instance_colour = this.get_instance_colour();
          let r = instance_colour.rgba.r
          let g = instance_colour.rgba.g
          let b = instance_colour.rgba.b
          const preStrokeStyle = ctx.strokeStyle;
          ctx.strokeStyle = preStrokeStyle;
          // 1) draw primary path
          if (points.length >= 1) {

            this.draw_label(ctx, points[0].x, points[0].y, instance)
            ctx.fillStyle = "rgba(" + r + "," + g + "," + b + `,${this.$props.default_instance_opacity})`;
            ctx.moveTo(points[0].x, points[0].y)

          }

          if (points.length >= 2) {
            this.draw_polygon_lines(instance, ctx, points)
            ctx.lineTo(points[0].x, points[0].y)
          }

          this.is_mouse_in_path(ctx, i, instance, figure_id) // must be seperate from when circles are drawn

          let spatial_line_size = this.get_spatial_line_size()
          if (spatial_line_size != 0) {
            ctx.lineWidth = spatial_line_size
            ctx.stroke()
          }

          // We may want these selection values to be user definable
          // Context of wanting a lower value when selected is so the person can still see the raw image
          // AND the overall coverage is still visible. Especially relevant if spatial_line is 0.
          if (instance.selected != "undefined" && instance.selected == true && this.$props.default_instance_opacity != 1) {
            ctx.fillStyle = "rgba(" + r + "," + g + "," + b + ", .1)";
          }

          if (this.instance_hover_index == i && this.$props.default_instance_opacity != 1) {
            ctx.fillStyle = "rgba(" + r + "," + g + "," + b + ",.1)";
          }

          if (instance.type == "polygon") {
            ctx.fill()
          }
          if (instance.type == "line") {
            ctx.lineWidth *= 2
          }
        },
        draw_polygon_main_section: function (instance, ctx, i) {

          let figure_id_list = [];

          for (const point of instance.points){
            if(!point.figure_id){
              continue
            }
            if(!figure_id_list.includes(point.figure_id)){
              figure_id_list.push(point.figure_id)
            }
          }
          if(figure_id_list.length === 0){
            let points = instance.points;
            this.draw_polygon_figure(instance, ctx, i, points)
          }
          else{
            for(const figure_id of figure_id_list){
              let points = instance.points.filter(p => p.figure_id === figure_id);
              this.draw_polygon_figure(instance, ctx, i, points, figure_id)
            }
          }



          return true
        },
        draw_polygon_control_points: function (instance, ctx, i) {
          ctx.beginPath();
          let points = instance.points
          if (instance.selected || instance.type == 'line' || this.$props.is_actively_drawing) {
            // Draw edit circles
            // isPointInPath() needs to be run twice then, once for
            // line path (ie clicking in middle of polygon) and once
            // for clicking on circles
            // prior when trying to run together did not detect in middle
            if (points.length >= 1) {
              ctx.fillStyle = '#ffffff';
              ctx.strokeStyle = '#bdbdbd';
              if (instance.points[0].hovered_while_drawing){
                ctx.fillStyle = 'white';
                ctx.strokeStyle = 'white';
              }
              if(instance.points[0].point_set_as_auto_border){
                ctx.fillStyle = '#4caf50';
                ctx.strokeStyle = '#4caf50';
              }
              this.draw_circle_from_instance(instance, points, 0, ctx)
            }
            if (points.length >= 2) {
              this.draw_many_polygon_circles(instance,i , ctx)
            }

            // Need to run this again otherwise edges of circles
            // outside of polygon won't be detected for edit which makes
            // edit break
            this.is_mouse_in_path(ctx, i, instance)

          }
          let spatial_line_size = this.get_spatial_line_size()
          if (this.$props.auto_border_polygon_p1) {
            this.draw_single_path_circle(this.$props.auto_border_polygon_p1.x,
              this.$props.auto_border_polygon_p1.y,
              this.circle_size,
              ctx,
              '#4caf50',
              '#4caf50',
              `${spatial_line_size}px`);
          }

          if (this.$props.auto_border_polygon_p2) {

            this.draw_single_path_circle(this.$props.auto_border_polygon_p2.x,
              this.$props.auto_border_polygon_p2.y,
              this.circle_size,
              ctx,
              '#4caf50',
              '#4caf50',
              `${spatial_line_size}px`)
          }

          ctx.stroke()
        },

        // point type  (not sub of polygon)

        draw_point: function (instance, ctx, i) {

          let point = instance.points[0]

          if (point == null) { return }

          let circle_size = 5 / this.canvas_transform['canvas_scale_combined']

          if (typeof this.colour == "undefined") {  return  }
          const instance_colour = this.get_instance_colour();
          let r = instance_colour.rgba.r
          let g = instance_colour.rgba.g
          let b = instance_colour.rgba.b

          this.draw_label(ctx, point.x, point.y, instance)

          ctx.fillStyle = "rgba(" + r + "," + g + "," + b + ",.75)";

          this.draw_circle(point.x, point.y, ctx)

          this.is_mouse_in_path(ctx, i, instance)   // caution must be after drawing path (ie circle)

          ctx.fill()

          ctx.stroke()

        },

        draw_cuboid_corner_circles: function(instance, ctx, i){
          let result = false;
          if (this.draw_mode == false) {
            if (this.mode == 'default') {
              const radius = (this.$props.vertex_size) / this.canvas_transform['canvas_scale_combined']
              this.draw_single_path_circle(instance.front_face.top_left.x  , instance.front_face.top_left.y , radius, ctx)
              if(this.is_mouse_in_path(ctx, i, instance)){ result = true}
              this.draw_single_path_circle(instance.front_face.top_right.x , instance.front_face.top_right.y ,radius, ctx)
              if(this.is_mouse_in_path(ctx, i, instance)){ result = true}
              this.draw_single_path_circle(instance.front_face.bot_left.x , instance.front_face.bot_left.y ,radius, ctx)
              if(this.is_mouse_in_path(ctx, i, instance)){ result = true}
              this.draw_single_path_circle(instance.front_face.bot_right.x , instance.front_face.bot_right.y ,radius, ctx)
              if(this.is_mouse_in_path(ctx, i, instance)){ result = true}
              this.draw_single_path_circle(instance.rear_face.top_left.x , instance.rear_face.top_left.y , radius, ctx)
              if(this.is_mouse_in_path(ctx, i, instance)){ result = true}
              this.draw_single_path_circle(instance.rear_face.top_right.x , instance.rear_face.top_right.y , radius, ctx)
              if(this.is_mouse_in_path(ctx, i, instance)){ result = true}
              this.draw_single_path_circle(instance.rear_face.bot_left.x , instance.rear_face.bot_left.y  , radius, ctx)
              if(this.is_mouse_in_path(ctx, i, instance)){ result = true}
              this.draw_single_path_circle(instance.rear_face.bot_right.x , instance.rear_face.bot_right.y  , radius, ctx)
              if(this.is_mouse_in_path(ctx, i, instance)){ result = true}
              const prevFill = ctx.fillStyle;
              ctx.fillStyle = 'white';
              ctx.fill()
              ctx.stroke()
              ctx.fillStyle = prevFill;
            }
          }
          return result
        },
        inside: function(point, vs, ctx){
          ctx.beginPath();
          for(var i = 0; i< vs.length ; i++){
            let current = vs[i]
            if(i == 0){
              ctx.moveTo(current.x, current.y)
              continue;
            }
            ctx.lineTo(current.x, current.y)
          }
          ctx.closePath();

          return ctx.isPointInPath(point.x, point.y);
        },
        is_point_in_cuboid_face: function(side, front_face, rear_face, ctx){
          if(!this.mouse_position){
            return false;
          }
          const mouse_x = this.mouse_position.raw.x;
          const mouse_y = this.mouse_position.raw.y;
          if(side === 'top'){
            const polygon = [
              front_face.top_left,
              front_face.top_right,
              rear_face.top_right,
              rear_face.top_left,
            ]
            return this.inside({x: mouse_x, y: mouse_y}, polygon, ctx)
          }
          else if(side === 'rear'){
            const polygon = [
              rear_face.top_right,
              rear_face.bot_right,
              rear_face.bot_left,
              rear_face.top_left,
            ]
            return this.inside({x: mouse_x, y: mouse_y}, polygon, ctx)
          }
          else if(side === 'front'){
            const polygon = [
              front_face.top_right,
              front_face.bot_right,
              front_face.bot_left,
              front_face.top_left,
            ]
            return this.inside({x: mouse_x, y: mouse_y}, polygon, ctx)
          }
          else if(side === 'right'){
            const polygon = [
              front_face.top_right,
              front_face.bot_right,
              rear_face.bot_right,
              rear_face.top_right,
            ]
            return this.inside({x: mouse_x, y: mouse_y}, polygon, ctx)
          }
          else if(side === 'left'){
            const polygon = [
              front_face.top_left,
              front_face.bot_left,
              rear_face.bot_left,
              rear_face.top_left,
            ]
            return this.inside({x: mouse_x, y: mouse_y}, polygon, ctx)
          }
          else if(side === 'bottom'){
            const polygon = [
              front_face.bot_left,
              front_face.bot_right,
              rear_face.bot_right,
              rear_face.bot_left,
            ]
            return this.inside({x: mouse_x, y: mouse_y}, polygon, ctx)
          }
          return false
        },
        detect_hover_on_cuboid: function (instance, ctx, i, hover_corner) {
          if(this.$props.is_actively_resizing){
            this.instance_hover_index = this.previous_instance_hover_index;
            this.count_instance_in_ctx_paths +=1;
            this.cuboid_hovered_face = this.prev_cuboid_hovered_face;
            return
          }
          const hover_front_face = this.is_point_in_cuboid_face('front', instance.front_face, instance.rear_face, ctx);
          const hover_rear_face = this.is_point_in_cuboid_face('rear', instance.front_face, instance.rear_face, ctx);
          const hover_top_face = this.is_point_in_cuboid_face('top', instance.front_face, instance.rear_face, ctx);
          const hover_left_face = this.is_point_in_cuboid_face('left', instance.front_face, instance.rear_face, ctx);
          const hover_right_face = this.is_point_in_cuboid_face('right', instance.front_face, instance.rear_face, ctx);
          const hover_bottom_face = this.is_point_in_cuboid_face('bottom', instance.front_face, instance.rear_face, ctx);

          // if(hover_top_face){
          //   // Hover Top Face
          //   this.$cuboid.draw_cuboid_top_face(instance.front_face, instance.rear_face, ctx, true);
          // }

          if(instance.selected){
            ctx.beginPath();
            if (hover_rear_face) {
              const instance_colour = this.get_instance_colour();
              let r = instance_colour.rgba.r
              let g = instance_colour.rgba.g
              let b = instance_colour.rgba.b
              ctx.fillStyle = "rgba(" + r + "," + g + "," + b + ", 0.7)";
              this.$cuboid.draw_cuboid_face(instance.rear_face, ctx, true)
              this.cuboid_hovered_face = 'rear';
            } else if (hover_left_face) {
              // Hover Left Face
              this.$cuboid.draw_cuboid_left_face(instance.front_face, instance.rear_face, ctx, true)
              this.cuboid_hovered_face = 'left';
            } else if (hover_right_face) {
              // Hover Right Face
              this.$cuboid.draw_cuboid_right_face(instance.front_face, instance.rear_face, ctx, true)
              this.cuboid_hovered_face = 'right';
            } else if (hover_bottom_face) {
              // Hover Bottom Face
              this.$cuboid.draw_cuboid_down_face(instance.front_face, instance.rear_face, ctx, true)
              this.cuboid_hovered_face = 'bottom';
            }
            else if (hover_top_face) {
              // Hover Bottom Face
              this.$cuboid.draw_cuboid_top_face(instance.front_face, instance.rear_face, ctx, true)
              this.cuboid_hovered_face = 'top';
            }

          }



          if (hover_top_face || hover_left_face || hover_right_face
            || hover_bottom_face || hover_rear_face || hover_front_face || hover_corner) {
            if (this.instance_hover_index != i) {
              this.instance_hover_index = i
              this.instance_hover_type = instance.type
            }
            this.count_instance_in_ctx_paths += 1
          }
        },
        detect_hover_on_ellipse: function(instance, ctx, i){
          if(!this.mouse_position){
            return
          }
          const point = this.mouse_position.raw;
          if(ctx.isPointInPath(point.x, point.y)){
            this.count_instance_in_ctx_paths += 1;
            this.instance_hover_index = i;
            this.instance_hover_type = instance.type;
          }
          // Detect Hover Circle

        },
        draw_single_path_circle: function(x, y, radius, ctx, strokeStyle = '#bdbdbd', fillStyle= 'white', lineWidth='2px'){
          ctx.beginPath();
          ctx.strokeStyle = strokeStyle;
          ctx.fillStyle = fillStyle;
          ctx.lineWidth = lineWidth;
          ctx.arc(x, y, radius, 0, 2 * Math.PI);
          ctx.fill()
          ctx.stroke()
        },
        draw_control_points_and_detect_hover: function(instance, ctx, i){
          let circle_size = ( this.$props.vertex_size) / this.canvas_transform['canvas_scale_combined']
          if(circle_size <= 0){
            return
          }
          const mouse = this.mouse_position.raw;
          // do we want to cache and then restore lineWidth or something?
          // or can it just be the same?
          ctx.lineWidth = this.get_spatial_line_size()
          this.draw_single_path_circle(instance.p1.x, instance.p1.y, circle_size, ctx)
          const hover_cp1 = ctx.isPointInPath(mouse.x, mouse.y);

          this.draw_single_path_circle(instance.cp.x, instance.cp.y, circle_size, ctx);
          const hover_cpmid = ctx.isPointInPath(mouse.x, mouse.y);

          this.draw_single_path_circle(instance.p2.x, instance.p2.y, circle_size, ctx)
          const hover_cp2 = ctx.isPointInPath(mouse.x, mouse.y);
          // Draw lines to control point
          ctx.setLineDash([3]);
          ctx.moveTo(instance.p1.x, instance.p1.y);
          if(instance.selected){
            ctx.strokeStyle = 'rgba(189,189,189,0.4)';
            ctx.lineTo(instance.cp.x, instance.cp.y)
            ctx.stroke();
            ctx.setLineDash([3]);
            ctx.moveTo(instance.p2.x, instance.p2.y);

            ctx.lineTo(instance.cp.x, instance.cp.y)
            ctx.stroke()
          }

          if (hover_cp1 || hover_cpmid || hover_cp2) {
            if (this.instance_hover_index != i) {
              this.instance_hover_index = i
              this.instance_hover_type = instance.type
            }
            this.count_instance_in_ctx_paths += 1
          }
        },

        draw_cuadratic_curve(instance, ctx, i){

          const mouse = this.mouse_position.raw;
          ctx.beginPath();
          ctx.moveTo(instance.p1.x, instance.p1.y)
          ctx.quadraticCurveTo(instance.cp.x, instance.cp.y, instance.p2.x, instance.p2.y);
          ctx.stroke();
          // Line hover detection
          if(ctx.isPointInPath(mouse.x, mouse.y)){
            if (this.instance_hover_index != i) {
              this.instance_hover_index = i
              this.instance_hover_type = instance.typedetect_hover_on_cuboid
            }
            this.count_instance_in_ctx_paths += 1
          }


          this.draw_control_points_and_detect_hover(instance, ctx, i);
        },
        draw_ellipse_corner_circles: function(instance, ctx, i){
          let result = false;
          if (this.draw_mode == false) {
            if (this.mode == 'default') {
              if(!instance.angle){
                instance.angle = 0
              }
              let a = instance.width;
              let b = instance.height;
              const radius = ( this.$props.vertex_size) / this.canvas_transform['canvas_scale_combined']
              this.$ellipse.generate_ellipse_corners(instance, a, b)

              //right
              this.draw_single_path_circle(instance.corners.right.x, instance.corners.right.y, radius, ctx)
              if(this.is_mouse_in_path(ctx, i, instance)){ result = true}
              // left
              this.draw_single_path_circle(instance.corners.left.x, instance.corners.left.y, radius, ctx)
              if(this.is_mouse_in_path(ctx, i, instance)){ result = true}
              // top
              this.draw_single_path_circle(instance.corners.top.x, instance.corners.top.y , radius, ctx)
              if(this.is_mouse_in_path(ctx, i, instance)){ result = true}
              // bot
              this.draw_single_path_circle(instance.corners.bot.x, instance.corners.bot.y , radius, ctx)
              if(this.is_mouse_in_path(ctx, i, instance)){ result = true}
              // rotate point

              this.draw_single_path_circle(instance.corners.rotate.x, instance.corners.rotate.y , radius + 4, ctx, 'blue', '4px')
              if(this.is_mouse_in_path(ctx, i, instance)){ result = true}
              // top right
              this.draw_single_path_circle(instance.corners.top_right.x, instance.corners.top_right.y , radius, ctx)
              if(this.is_mouse_in_path(ctx, i, instance)){ result = true}
              // bot_right
              this.draw_single_path_circle(instance.corners.bot_right.x, instance.corners.bot_right.y , radius, ctx)
              if(this.is_mouse_in_path(ctx, i, instance)){ result = true}
              // top_left
              this.draw_single_path_circle(instance.corners.top_left.x, instance.corners.top_left.y , radius, ctx)
              if(this.is_mouse_in_path(ctx, i, instance)){ result = true}
              // bot_left
              this.draw_single_path_circle(instance.corners.bot_left.x, instance.corners.bot_left.y , radius, ctx)
              if(this.is_mouse_in_path(ctx, i, instance)){ result = true}
            }
          }
          return result
        },
        draw_ellipse: function(instance, ctx, i){
          const instance_colour = this.get_instance_colour();
          let r = instance_colour.rgba.r
          let g = instance_colour.rgba.g
          let b = instance_colour.rgba.b
          ctx.fillStyle = `rgba(${r},${g},${b}, 0.1)`;
          this.$ellipse.draw_ellipse(
            instance,
            ctx
          )

          this.detect_hover_on_ellipse(instance, ctx, i);
          if(instance.selected){
            this.draw_ellipse_corner_circles(instance, ctx);
          }
        },
        draw_cuboid: function (instance, ctx, i) {
          /* instance, current instance object
           * ctx
           * draws the front and back cuboid faces,
           * then draws the 4 side lines
           */
          const instance_colour = this.get_instance_colour();
          let r = instance_colour.rgba.r
          let g = instance_colour.rgba.g
          let b = instance_colour.rgba.b


          ctx.stokeStyle = "rgba(" + r + "," + g + "," + b + ", 1)";
          ctx.fillStyle = "rgba(" + r + "," + g + "," + b + ", 0)";
          this.$cuboid.draw_cuboid_face(instance.front_face, ctx, false)
          // Rear face has fill
          ctx.fillStyle = "rgba(" + r + "," + g + "," + b + ", .4)";
          this.$cuboid.draw_cuboid_face(instance.rear_face, ctx, true)

          // Lateral Faces
          // Top Face
          this.$cuboid.draw_cuboid_top_face(instance.front_face, instance.rear_face, ctx, false);
          // Left Face
          this.$cuboid.draw_cuboid_left_face(instance.front_face, instance.rear_face, ctx, false)
          // Right Face
          this.$cuboid.draw_cuboid_right_face(instance.front_face, instance.rear_face, ctx, false)
          // Bottom Face
          this.$cuboid.draw_cuboid_down_face(instance.front_face, instance.rear_face, ctx, false)
          ctx.stroke();

          let hover_corner = false
          if(instance.selected){
            hover_corner = this.draw_cuboid_corner_circles(instance, ctx, i);
          }
          this.detect_hover_on_cuboid(instance, ctx, i, hover_corner);

          return true

        },

        draw_label: function (ctx, x, y, instance) {
          /* There's a lot of random stuff we may want to
           * draw about something. I wonder if we are better to just place it all
           * into one string...
           * I think for now let's simplify to a message
           * and can get more fancy later if we want
           */

          if ( this.label_settings == null
               || this.label_settings.show_text == false
               || instance == undefined) {
            return
          }

          let message = ""

          if (this.label_settings.show_label_text == true) {
            message += instance.label_file.label.name
            if (instance.number != undefined) {
              message += " " + instance.number
            }
          }

          if (this.label_settings.show_attribute_text == true) {
            if (instance.attribute_groups) {
             for (const [id, attribute] of Object.entries(instance.attribute_groups)) {
               if (attribute && attribute['display_name']) {
                 message += " " + attribute['display_name']
               }
              }
            }
          }

          if (instance.missing) {
            if (instance.missing == true) {
               message += " Missing"
            }
          }

          if (  instance.soft_delete
             && instance.soft_delete == true) {
            message += " Removed"
          }

          if (  instance.interpolated
             && instance.interpolated == true) {
            message += " Interpolated"
          }


          ctx.fillStyle = this.$get_sequence_color(instance.sequence_id)

          this.draw_text(ctx, message, x, y, ctx.font,
            '255, 255, 255,',
            this.$props.label_settings.font_background_opacity);
        },

        draw_text(ctx, message, x, y, font, background_color, background_opacity) {

          ctx.textBaseline = 'bottom'
          ctx.font = font

          let text_width = ctx.measureText(message).width;

          let previous_style = ctx.fillStyle
          ctx.fillStyle = "rgba(" + background_color + background_opacity + ")";

          let text_height = parseInt(font, 10)
          // the `y - text_height` assumes textBaseline = 'bottom', it's not needed if textBaseline = 'top'
          let padding = 2
          ctx.fillRect(
            x - 1,
            y - text_height - padding,
            text_width + padding,
            text_height + padding)

          ctx.fillStyle = previous_style

          ctx.fillText(message, x, y);

        },

        get_instance_colour(){
          let colour_result =  {
            rgba: {
              r: 255,
              g: 255,
              b: 255,
            }
          }
          colour_result.rgba.r = this.colour.rgba.r
          colour_result.rgba.g = this.colour.rgba.g
          colour_result.rgba.b = this.colour.rgba.b
          if(this.$store.state.annotation_state.instance_select_for_issue){
            colour_result.rgba.r = 255;
            colour_result.rgba.g = 255;
            colour_result.rgba.b = 255;

          }
          return colour_result
        },
        draw_box_edit_corners: function (ctx, i, instance) {

          if (this.draw_mode == false && (this.previous_instance_hover_index == i || instance.selected)) {
            if (this.mode == 'default') {

              this.draw_circle(instance.x_min, instance.y_min, ctx)
              ctx.moveTo(instance.x_max, instance.y_min);
              this.draw_circle(instance.x_max, instance.y_min, ctx)
              ctx.moveTo(instance.x_max, instance.y_max);
              this.draw_circle(instance.x_max, instance.y_max, ctx)
              ctx.moveTo(instance.x_min, instance.y_max);
              this.draw_circle(instance.x_min, instance.y_max, ctx)
              ctx.fill()
            }
          }
        },

        draw_box: function (instance, ctx, i) {

          // possible to refactor this into a "draw face" function?
          const instance_colour = this.get_instance_colour();

          let r = instance_colour.rgba.r
          let g = instance_colour.rgba.g
          let b = instance_colour.rgba.b


          this.draw_label(ctx, instance.x_min, instance.y_min, instance)

          // start Focus instance feature
          var opacity =  this.$props.default_instance_opacity;

          /*
          // TODO this is confusing if we are just focusing one instance a time
          if (this.instance_focused_index) {
            if (instance.id == this.instance_focused_index) {
              opacity = .35
            } else {
              opacity = .1
            }
          }
          */
          // end Focus feature
          if (this.mode == 'gold_standard') {
            ctx.fillStyle = "rgba(255, 215, 0," + opacity + ")";
          }
          if (this.mode == 'default') {
            ctx.fillStyle = "rgba(" + r + "," + g + "," + b + "," + opacity + ")";

          }

          ctx.rect(
            this.toInt(instance.x_min),
            this.toInt(instance.y_min),
            this.toInt(instance.width),
            this.toInt(instance.height))

          ctx.stroke()

          ctx.fill()


          this.is_mouse_in_path(ctx, i, instance)

          // after we know if it's in path
          this.draw_box_edit_corners(ctx, i, instance)

          // run again so we still capture the corners for editing
          this.is_mouse_in_path(ctx, i, instance)

        },

         // inspired by http://jsfiddle.net/m1erickson/8j6kdf4o/
        drawStar: function (cx, cy, spikes, outerRadius, innerRadius, ctx) {

          var rot = Math.PI / 2 * 3;
          var x = cx;
          var y = cy;
          var step = Math.PI / spikes;

          ctx.moveTo(cx, cy - outerRadius)

          for (let i = 0; i < spikes; i++) {

            x = cx + Math.cos(rot) * outerRadius;
            y = cy + Math.sin(rot) * outerRadius;
            ctx.lineTo(x, y)
            rot += step

            x = cx + Math.cos(rot) * innerRadius;
            y = cy + Math.sin(rot) * innerRadius;
            ctx.lineTo(x, y)
            rot += step
          }

          ctx.lineTo(cx, cy - outerRadius)

          ctx.stroke()
          ctx.closePath();

          ctx.fill()

        },

        draw_gold_standard: function () {

          // TODO move gold standard functions here if possible

        },

        point_is_intersecting_circle: function (mouse, point) {
          // Careful this is effected by scale

            // bool, true if point if intersecting circle
            let radius = 8 / this.canvas_transform['canvas_scale_combined']

            return Math.sqrt(
                (point.x - mouse.x) ** 2
              + (mouse.y - point.y) ** 2) < radius  // < number == circle.radius
        },
      },
      computed:{
         instance_select_for_issue: function(){
           return this.$store.getters.get_instance_select_for_issue;
         },
         view_issue_mode: function(){
           return this.$store.getters.get_view_issue_mode;
         }
      }
    })


 </script>
