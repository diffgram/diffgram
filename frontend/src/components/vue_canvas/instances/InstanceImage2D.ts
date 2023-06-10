import {Instance} from "./Instance";
import {MousePosition} from "../../../types/mouse_position";
import {ImageCanvasTransform} from "../../../types/CanvasTransform";
import {ImageLabelSettings} from "../../../types/image_label_settings";
import {get_sequence_color} from '../../regular/regular_annotation'
import {CanvasMouseTools} from "../CanvasMouseTools";

export abstract class InstanceImage2D extends Instance {
  public ctx: CanvasRenderingContext2D;
  public canvas_transform: ImageCanvasTransform;
  public canvas_element: HTMLCanvasElement
  public strokeColor: string = 'black';
  public line_width: number = 4;
  public fillColor: string = 'white';
  public image_label_settings: ImageLabelSettings
  public is_moving: boolean = false;
  protected is_actively_drawing: boolean = false;
  protected has_changed: boolean = false;
  public canvas_mouse_tools: CanvasMouseTools;
  private previous_label_file_id: number = undefined;

  public get_canvas_transform(): ImageCanvasTransform {
    return this.canvas_transform
  }

  public set_actively_drawing(val: boolean): void {
    this.is_actively_drawing = val
  }

  public get_is_actively_drawing(): boolean {
    return this.is_actively_drawing;
  }

  public set_is_resizing(val: boolean) {
    this.is_resizing = val
  }

  public set_is_moving(val: boolean) {
    this.is_moving = val
  }

  public remove_listener(event_type: string, callback: Function) {
    if (event_type === 'hover_in') {
      this.on_instance_hovered = null
    }
    if (event_type === 'hover_out') {
      this.on_instance_unhovered = null
    }
  }

  public set_color_from_label() {

    if (this.previous_label_file_id == this.label_file_id) { return }

    let colour = this.get_label_file_colour_map()[this.label_file_id]

    if (colour) {
      this.set_border_color(colour.hex)
      this.set_fill_color(colour.rgba.r, colour.rgba.g, colour.rgba.b, 0.1)
      this.previous_label_file_id = this.label_file_id // cache for speed
    }

    return true
  }

  public set_border_color(colorHex: string) {
    this.strokeColor = colorHex
  }

  public set_fill_color(r: number, g: number, b: number, a: number) {
    this.fillColor = "rgba(" + r + "," + g + "," + b + "," + a + ")";
  }

  protected get_color_from_instance(ctx: CanvasRenderingContext2D) {

    if(this.fillColor != ctx.fillStyle){
      ctx.fillStyle = this.fillColor
    }
    if(this.strokeColor != ctx.strokeStyle){
      ctx.strokeStyle = this.strokeColor
    }
  }

  public set_canvas(val: HTMLCanvasElement) {
    this.canvas_element = val
    if (this.canvas_element) {
      this.ctx = this.canvas_element.getContext("2d");
    }
  }

  public set_sequence_id(val: number) {
    this.sequence_id = val
  }

  public set_sequence_number(val: number) {
    this.number = val
  }

  public set_canvas_transform(val: ImageCanvasTransform) {
    this.canvas_transform = val
  }
  public set_canvas_mouse_tools(val: CanvasMouseTools) {
    this.canvas_mouse_tools = val
  }

  public set_image_label_settings(val: ImageLabelSettings) {
    this.image_label_settings = val
  }


  public draw_text(ctx, message, x, y, font, background_color, background_opacity) {
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
  }

  public draw_label(ctx, x, y) {
    if (this.image_label_settings == null
      || this.image_label_settings.show_text == false) {
      return
    }

    let message = ""
    if (this.image_label_settings.show_label_text == true &&
      this.label_file.label) {
      message += this.label_file.label.name
      if (this.number != undefined) {
        message += " " + this.number
      }
    }

    if (this.image_label_settings.show_attribute_text == true) {
      if (this.attribute_groups) {
        for (const [id, attribute] of Object.entries(this.attribute_groups)) {
          if (attribute && attribute['display_name']) {
            message += " " + attribute['display_name']
          }
        }
      }
    }

    if (this.soft_delete
      && this.soft_delete == true) {
      message += " Removed"
    }

    if (this.interpolated
      && this.interpolated == true) {
      message += " Interpolated"
    }


    ctx.fillStyle = get_sequence_color(this.sequence_id)

    this.draw_text(ctx, message, x, y, ctx.font,
      '255, 255, 255,',
      this.image_label_settings.font_background_opacity);
  }

  protected is_mouse_in_path(ctx) {
    if(!this.canvas_mouse_tools){
      return false
    }
    if(!this.canvas_mouse_tools.mouse_position){
      return false
    }
    let mouse_position = this.canvas_mouse_tools.mouse_position;
    if (!mouse_position || !mouse_position.raw) {
      return false
    }
    if (ctx.isPointInPath(
      mouse_position.raw.x,
      mouse_position.raw.y)) {
      return true;
    }
    return false
  }

  protected update_width_and_height() {
    this.width = this.x_max - this.x_min;
    this.height = this.y_max - this.y_min;

    this.width = Math.ceil(this.width)
    this.height = Math.ceil(this.height)
    this.status = "updated";
  }

  protected get_spatial_line_size(){
    let size = this.image_label_settings.spatial_line_size

    return size
  }
  public get_instance_data(): any {
    let res = super.get_instance_data();
    return {
      ...res,
      strokeColor: this.strokeColor,
      fillColor: this.fillColor,
    }
  }

}
