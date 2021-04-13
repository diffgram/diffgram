

export class ellipse {
  get_x_of_rotated_ellipse(t, instance, angle=undefined){
    let rot_angle = angle != undefined ? angle : instance.angle ;
    let h = instance.center_x;
    let k = instance.center_y;
    let a = instance.width;
    let b = instance.height;
    let x = h + a*Math.cos(t) * Math.cos(rot_angle) - b * Math.sin(t) * Math.sin(rot_angle)
    return x
  }

  get_y_of_rotated_ellipse(t, instance, angle=undefined){
    let rot_angle = angle != undefined ? angle : instance.angle ;
    let h = instance.center_x;
    let k = instance.center_y;
    let a = instance.width;
    let b = instance.height;
    let y = k + b*Math.sin(t) * Math.cos(rot_angle) + a * Math.cos(t) * Math.sin(rot_angle)
    return y
  }
  generate_ellipse_corners(instance, a, b){
    /*
    * instance: the current instance to generate corners.
    * a: major edge of the ellipse
    * b: minor edge of the ellipse
    *
    * */
    instance.corners = {}
    //right
    let t = Math.atan(-(b) *  Math.tan(instance.angle))/ (a);
    let x_right = this.get_x_of_rotated_ellipse(t, instance)
    let y_right = this.get_y_of_rotated_ellipse(t, instance)
    instance.corners.right = {x: x_right, y: y_right}
    // left
    let t1 = t + Math.PI;
    let x_left = this.get_x_of_rotated_ellipse(t1, instance)
    let y_left = this.get_y_of_rotated_ellipse(t1, instance)
    instance.corners.left = {x: x_left, y: y_left}
    // top
    t1 = t + Math.PI + (Math.PI / 2);
    let x_top = this.get_x_of_rotated_ellipse(t1, instance)
    let y_top = this.get_y_of_rotated_ellipse(t1, instance)
    instance.corners.top = {x: x_top, y: y_top}
    // bot
    t1 = t + (Math.PI / 2);
    let x_bot = this.get_x_of_rotated_ellipse(t1, instance)
    let y_bot = this.get_y_of_rotated_ellipse(t1, instance)
    instance.corners.bot = {x: x_bot, y: y_bot}
    // Rotate point
    let v = {x: instance.center_x - x_top, y: instance.center_y - y_top};
    let v_len = Math.sqrt( v.x ** 2 + v.y ** 2);
    let u = {x: v.x / v_len, y: v.y / v_len};
    instance.corners.rotate = {
      x: x_top - 80 * (u.x),  // The point along a line at a distance d (d=20) is => (x0, y0) + d*u
      y: y_top - 80 * (u.y)
    }
    // Bounding box corners
    instance.corners.top_right = {
      x: x_top + (x_right - instance.center_x),
      y: y_top + (y_right - instance.center_y)
    }
    instance.corners.top_left = {
      x: x_top + (x_left - instance.center_x),
      y: y_top + (y_left - instance.center_y)
    }
    instance.corners.bot_right = {
      x: x_bot + (x_right - instance.center_x),
      y: y_bot + (y_right - instance.center_y)
    }
    instance.corners.bot_left = {
      x: x_bot + (x_left - instance.center_x),
      y: y_bot + (y_left - instance.center_y)
    }
  }

  draw_ellipse(instance, ctx){
    ctx.ellipse(
      instance.center_x,
      instance.center_y,
      instance.width,
      instance.height,
      instance.angle ? instance.angle : 0,
      0,
      2 * Math.PI)

    ctx.fill();
    ctx.stroke()
  }
}


