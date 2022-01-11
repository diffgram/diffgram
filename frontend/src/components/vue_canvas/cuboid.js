

export class cuboid {

draw_cuboid_side_line(a_point, b_point, ctx, lineDash = 0) {
  ctx.setLineDash([lineDash])
  ctx.moveTo(a_point.x, a_point.y)
  ctx.lineTo(b_point.x, b_point.y)

};

draw_line(b_point, ctx, lineDash = 0) {

  ctx.setLineDash([lineDash])
  ctx.lineTo(b_point.x, b_point.y)

};

draw_cuboid_top_face(front_face, rear_face, ctx, fill=false, lineDash = 0){
  // Drawing lines for Top Face
  ctx.setLineDash([lineDash])
  this.draw_cuboid_side_line(front_face.top_right, front_face.top_left, ctx, lineDash)
  // this.draw_line(rear_face.top_left, ctx, lineDash)
  // this.draw_line(rear_face.top_right, ctx, lineDash)
  // this.draw_line(front_face.top_right, ctx, lineDash)
  if(fill){
    ctx.globalAlpha = 1;
    ctx.fillStyle = "rgba(" + 117 + "," + 117 + "," + 117 + ", 0.4";
    ctx.fill();
  }
};
draw_cuboid_left_face(front_face, rear_face, ctx, fill=false, lineDash = 0){
  // Drawing lines for Right Face
  ctx.setLineDash([lineDash])
  this.draw_cuboid_side_line(front_face.top_left, rear_face.top_left, ctx, lineDash)
  this.draw_line(rear_face.bot_left, ctx, lineDash)
  this.draw_line(front_face.bot_left, ctx, lineDash)
  this.draw_line(front_face.top_left, ctx, lineDash)
  if(fill){
    ctx.globalAlpha = 1;
    ctx.fillStyle = "rgba(" + 117 + "," + 117 + "," + 117 + ", 0.4";
    ctx.fill();
  }

};
draw_cuboid_right_face(front_face, rear_face, ctx, fill=false, lineDash = 0){
  // Drawing lines for Left Face
  ctx.setLineDash([lineDash])
  this.draw_cuboid_side_line(front_face.top_right, rear_face.top_right, ctx, lineDash)
  this.draw_line(rear_face.bot_right, ctx, lineDash)
  this.draw_line(front_face.bot_right, ctx, lineDash)
  this.draw_line(front_face.top_right, ctx, lineDash)
  if(fill){
    ctx.globalAlpha = 1;
    ctx.fillStyle = "rgba(" + 117 + "," + 117 + "," + 117 + ", 0.4";
    ctx.fill();
  }
};
draw_cuboid_down_face(front_face, rear_face, ctx, fill=false, lineDash = 0){
  // Drawing lines for Down Face
  ctx.setLineDash([lineDash])
  // this.draw_cuboid_side_line(front_face.bot_left, rear_face.bot_left, ctx, lineDash)
  // this.draw_line(rear_face.bot_right, ctx, lineDash)
  // this.draw_line(front_face.bot_right, ctx, lineDash)
  // this.draw_line(front_face.bot_left, ctx, lineDash)
  if(fill){
    ctx.globalAlpha = 1;
    ctx.fillStyle = "rgba(" + 117 + "," + 117 + "," + 117 + ", 0.4";
    ctx.fill();
  }
};

draw_cuboid_sides (front_face, rear_face, ctx, lineDash = 0) {
  /* front_face, object of 4 points
    * rear_face, object of 4 points
    * ctx
    *
    * Draws the side lines of a cuboid
    * */
  // We separate into 4 function to be able to detect hover events on each face separately.
  ctx.setLineDash([lineDash])
  this.draw_cuboid_top_face(front_face, rear_face, ctx, lineDash);
  this.draw_cuboid_right_face(front_face, rear_face, ctx, lineDash);
  this.draw_cuboid_left_face(front_face, rear_face, ctx, lineDash);
  this.draw_cuboid_down_face(front_face, rear_face, ctx, lineDash);

};

draw_cuboid_face (face, ctx, fill_face = false, lineDash = 0) {
  ctx.setLineDash([lineDash])
  ctx.beginPath();
  ctx.moveTo(face.top_left.x, face.top_left.y)
  ctx.lineTo(face.top_right.x, face.top_right.y)
  ctx.lineTo(face.bot_right.x, face.bot_right.y)
  ctx.lineTo(face.bot_left.x, face.bot_left.y)
  ctx.lineTo(face.top_left.x, face.top_left.y)
  ctx.closePath();
  if(fill_face === true){
    ctx.fill();
  }


};

}


