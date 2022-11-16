import {Instance} from "./Instance";
import {MousePosition} from "../../../types/mouse_position";
import {ImageCanvasTransform} from "../../../types/CanvasTransform";
import {ImageLabelSettings} from "../../../types/image_label_settings";
import {get_sequence_color} from '../../regular/regular_annotation'

export abstract class InstanceImage2D extends Instance {
  public ctx: CanvasRenderingContext2D;
  public mouse_position: MousePosition;
  public canvas_transform: ImageCanvasTransform;
  public canvas_element: HTMLCanvasElement
  public strokeColor: string = 'black';
  public fillColor: string = 'white';
  public image_label_settings: ImageLabelSettings

  public set_color_from_label() {
    let colour = this.get_label_file_colour_map()[this.label_file_id]
    if (colour) {
      this.set_border_color(colour.hex)
      this.set_fill_color(colour.rgba.r, colour.rgba.g, colour.rgba.b, 0.1)
    }
  }

  public set_border_color(colorHex: string) {
    this.strokeColor = colorHex
  }

  public set_fill_color(r: number, g: number, b: number, a: number) {
    this.fillColor = "rgba(" + r + "," + g + "," + b + "," + a + ")";
  }

  protected grab_color_from_instance(ctx: CanvasRenderingContext2D) {
    ctx.fillStyle = this.fillColor
    ctx.strokeStyle = this.strokeColor
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

  public set_image_label_settings(val: ImageLabelSettings) {
    this.image_label_settings = val
  }


  public draw_text(ctx, message, x, y, font, background_color, background_opacity){
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

  public draw_label(ctx, x, y){
    if ( this.image_label_settings == null
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

    if (  this.soft_delete
      && this.soft_delete == true) {
      message += " Removed"
    }

    if (  this.interpolated
      && this.interpolated == true) {
      message += " Interpolated"
    }


    ctx.fillStyle = get_sequence_color(this.sequence_id)
    this.draw_text(ctx, message, x, y, ctx.font,
      '255, 255, 255,',
      this.image_label_settings.font_background_opacity);
  }

  protected is_mouse_in_path(ctx) {
    if (!this.mouse_position || !this.mouse_position.raw) {
      return false
    }
    if (ctx.isPointInPath(
      this.mouse_position.raw.x,
      this.mouse_position.raw.y)) {
      return true;
    }
    return false
  }

  public get_instance_data(): any {
    let res = super.get_instance_data();
    return  {
      ...res,
      strokeColor: this.strokeColor,
      fillColor: this.fillColor,
    }
  }

}
