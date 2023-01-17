import {isBoolean} from "lodash";
import InstanceStore from "../helpers/InstanceStore";
import {Label, LabelFile, LabelFileMap} from "./label";
import {LabelColourMap} from "./label_colour_map";
import {Schema} from "./Schema";
import {Instance} from "../components/vue_canvas/instances/Instance";
import IssuesAnnotationUIManager from "../components/annotation/issues/IssuesAnnotationUIManager";
import {ModelRun} from "./models";
import {Task} from "./Task";
import {createDefaultLabelSettings, ImageLabelSettings} from "./image_label_settings";


export class BaseAnnotationUIContext {
  working_file: File
  working_file_list: File[]
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
  command_manager: any

  image_annotation_ctx: ImageAnnotationUIContext

  constructor() {
    this.working_file = null
    this.working_file_list = []
    this.task = null
    this.instance_type = 'box'
    this.instance_store = null
    this.per_instance_attribute_groups_list = []
    this.global_attribute_groups_list = []
    this.current_global_instance = undefined
    this.label_schema = null
    this.current_label_file = null
    this.selected_instance_for_history = null
    this.model_run_list = null
    this.issues_ui_manager = null
    this.image_annotation_ctx = new ImageAnnotationUIContext()
  }

}

export class ImageAnnotationUIContext {
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
  instance_buffer_metadata: object
  annotations_loading: boolean
  go_to_keyframe_loading: boolean
  save_multiple_frames_error: object

  get_userscript: Function

  constructor() {
    this.show_context_menu = false
    this.loading = false
    this.refresh = new Date()
    this.video_mode = false
    this.draw_mode = true
    this.current_frame = 0
    this.video_playing = false
    this.request_change_current_instance = null
    this.trigger_refresh_current_instance = null
    this.event_create_instance = null
    this.get_userscript = null
    this.label_settings = createDefaultLabelSettings()
    this.instance_buffer_metadata = {}
    this.annotations_loading = false
    this.go_to_keyframe_loading = false
    this.save_multiple_frames_error = {}
  }

}
