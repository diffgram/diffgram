
export type ImageLabelSettings = {
  font_background_opacity: number
  enable_snap_to_instance: boolean
  show_ghost_instances:  boolean
  show_text: boolean
  show_label_text: boolean
  show_attribute_text: boolean
  show_list: boolean
  show_occluded_keypoints: boolean
  show_left_right_arrows: boolean
  allow_multiple_instance_select: boolean
  font_size: number
  spatial_line_size: number,
  vertex_size: number,
  show_removed_instances: boolean,
  target_reticle_size: number,
  filter_brightness: number, // Percentage. Applies a linear multiplier to the drawing, making it appear more or less bright.
  filter_contrast: number, // Percentage. A value of 0% will create a drawing that is completely black. A value of 100% leaves the drawing unchanged.
  filter_grayscale: number, //  A value of 100% is completely gray-scale. A value of 0% leaves the drawing unchanged.
  instance_buffer_size: number,
  max_image_buffer: number,
  canvas_scale_global_is_automatic: boolean,
  canvas_scale_global_setting: number,
  left_nav_width: number,
  on_instance_creation_advance_sequence: boolean,
  ghost_instances_closed_by_open_view_edit_panel: boolean,
  smooth_canvas: boolean
}

export function createDefaultLabelSettings(): ImageLabelSettings{
  return {
    font_background_opacity: 0.75,
    enable_snap_to_instance: true,
    show_ghost_instances: true,
    show_text: true,
    show_label_text: true,
    show_attribute_text: true,
    show_list: true,
    show_occluded_keypoints: true,
    show_left_right_arrows: false,
    allow_multiple_instance_select: false,
    font_size: 20,
    spatial_line_size: 2,
    vertex_size: 6,
    show_removed_instances: false,
    target_reticle_size: 20,
    filter_brightness: 100, // Percentage. Applies a linear multiplier to the drawing, making it appear more or less bright.
    filter_contrast: 100, // Percentage. A value of 0% will create a drawing that is completely black. A value of 100% leaves the drawing unchanged.
    filter_grayscale: 0, //  A value of 100% is completely gray-scale. A value of 0% leaves the drawing unchanged.
    instance_buffer_size: 60,
    max_image_buffer: 3,
    canvas_scale_global_is_automatic: true,
    canvas_scale_global_setting: 0.5,
    left_nav_width: 450,
    on_instance_creation_advance_sequence: true,
    ghost_instances_closed_by_open_view_edit_panel: false,
    smooth_canvas: true
  }
}
