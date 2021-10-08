

export const get_transformed_coordinates = function (point,
                                                     canvas_client,
                                                     canvas_element,
                                                     canvas_element_wrapper,
                                                     canvas_element_ctx){
  let x_raw = (point.x - canvas_client.left)
  let y_raw = (point.y - canvas_client.top)


  var target = canvas_element_wrapper,
    // style = target.currentStyle || window.getComputedStyle(target, null),
    // borderLeftWidth = parseInt(style["borderLeftWidth"], 10),
    // borderTopWidth = parseInt(style["borderTopWidth"], 10),
    rect = canvas_element_wrapper.getBoundingClientRect(),
    offsetX = point.x  - rect.left,
    offsetY = point.y  - rect.top;
  let canvas_width = canvas_element.width;
  let canvas_height = canvas_element.height;
  if(!canvas_width){
    canvas_width = canvas_element_wrapper.width;
    canvas_height = canvas_element_wrapper.height;
  }
  let x = (offsetX * canvas_width) / target.clientWidth;
  let y = (offsetY * canvas_height) / target.clientHeight;
  const ctx = canvas_element_ctx;
  console.log('CTXXXXX', ctx)
  var transform = ctx.getTransform();
  const invMat = transform.invertSelf();

  x = x * invMat.a + y * invMat.c + invMat.e;
  y = x * invMat.b + y * invMat.d + invMat.f;
  console.log('CANVAS UTILS TARGET', target)
  console.log('CANVAS UTILS TARGET', target.clientWidth, target.clientHeight)
  return {
    x: parseInt(x, 10),
    y: parseInt(y, 10),
    x_raw,
    y_raw
  }
}
