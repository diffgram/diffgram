import {isBoolean} from "lodash";
import InstanceStore from "../helpers/InstanceStore";
import {Label, LabelFile, LabelFileMap} from "./label";
import {LabelColourMap} from "./label_colour_map";
import {Schema} from "./Schema";
import {Instance} from "../components/vue_canvas/instances/Instance";
import IssuesAnnotationUIManager from "../components/annotation/issues/IssuesAnnotationUIManager";
import {ModelRun} from "./models";
import {Task} from "./Task";
import {ImageLabelSettings} from "./image_label_settings";


export class BaseAnnotationUIContext {
  working_file: File
  task: Task
  instance_type: string
  instance_store: InstanceStore
  per_instance_attribute_groups_list: object[]
  global_attribute_groups_list: object[]
  current_global_instance: object
  label_schema: Schema
  current_label_file: LabelFile
  selected_instance_for_history: Instance
  model_run_list: ModelRun[]
  issues_ui_manager: IssuesAnnotationUIManager

  image_annotation_ctx: ImageAnnotationUIContext

}

export class ImageAnnotationUIContext extends BaseAnnotationUIContext{
  show_context_menu: boolean
  loading: boolean
  refresh: Date
  video_mode: boolean
  draw_mode: boolean
  current_frame: number
  video_playing: boolean
  request_change_current_instance: number
  trigger_refresh_current_instance: Date

  event_create_instance: Instance
  label_settings: ImageLabelSettings
  instance_buffer_metadata: {number: object}
  annotations_loading: boolean

  get_userscript: Function

}
