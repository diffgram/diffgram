

export const get_transformed_coordinates = function (point, canvas_client, canvas_transform, canvas_translate){
  let x_raw = (point.x - canvas_client.left)
  let y_raw = (point.y - canvas_client.top)

  let x = (((x_raw - canvas_translate.x) / canvas_transform.canvas_scale_local) + canvas_translate.x) / canvas_transform.canvas_scale_global
  let y = (((y_raw - canvas_translate.y) / canvas_transform.canvas_scale_local) + canvas_translate.y) / canvas_transform.canvas_scale_global

  return {
    x: parseInt(x, 10),
    y: parseInt(y, 10),
    x_raw,
    y_raw
  }
}
