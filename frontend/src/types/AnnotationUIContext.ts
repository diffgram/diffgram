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
import {AttributeTemplateGroup} from "./attributes/AttributeTemplateGroup";
import {PanelsSettings} from "./attributes/PanelsSettings";

export type AnyAnnotationCtx =
  ImageAnnotationUIContext
  | AudioAnnotationUIContext
  | TextAnnotationUIContext
  | GeoAnnotationUIContext
  | SensorFusion3DAnnotationUIContext

export class BaseAnnotationUIContext {
  working_file: File
  working_file_list: File[]
  task: Task
  instance_type: string
  instance_store: InstanceStore
  per_instance_attribute_groups_list: object[]
  global_attribute_groups_list: AttributeTemplateGroup[]

  global_attribute_groups_list_compound: AttributeTemplateGroup[]
  compound_global_attributes_instance_list: Instance[]
  compound_global_instance_id: number
  compound_global_instance_index: number
  compound_global_instance: Instance
  current_global_instance: object
  label_schema: Schema
  current_label_file: LabelFile
  selected_instance_for_history: Instance
  model_run_list: ModelRun[]
  issues_ui_manager: IssuesAnnotationUIManager
  command_manager: any

  current_image_annotation_ctx: ImageAnnotationUIContext
  current_audio_annotation_ctx: AudioAnnotationUIContext
  current_text_annotation_ctx: TextAnnotationUIContext
  current_sensor_fusion_annotation_ctx: SensorFusion3DAnnotationUIContext
  current_geo_annotation_ctx: GeoAnnotationUIContext
  panel_settings: PanelsSettings
  num_rows: number
  num_cols: number

  hidden_label_id_list: number[]

  history: any

  public get_current_ann_ctx(): AnyAnnotationCtx {
    if (!this.working_file) {
      return undefined
    }
    let ref_name_map = {
      'image': this.current_image_annotation_ctx,
      'video': this.current_image_annotation_ctx,
      'audio': this.current_audio_annotation_ctx,
      'text': this.current_text_annotation_ctx,
      'geospatial': this.current_geo_annotation_ctx,
      'sensor_fusion': this.current_sensor_fusion_annotation_ctx,
    }
    return ref_name_map[this.working_file.type]
  }

  constructor() {
    this.working_file = null
    this.working_file_list = []
    this.task = null
    this.instance_type = 'box'
    this.instance_store = null
    this.per_instance_attribute_groups_list = []
    this.compound_global_attributes_instance_list = []
    this.global_attribute_groups_list = undefined
    this.global_attribute_groups_list_compound = undefined
    this.current_global_instance = undefined
    this.compound_global_instance = undefined
    this.label_schema = null
    this.current_label_file = null
    this.selected_instance_for_history = null
    this.model_run_list = null
    this.issues_ui_manager = null
    this.current_image_annotation_ctx = new ImageAnnotationUIContext()
    this.panel_settings = new PanelsSettings(1, 4)
    this.num_rows = 1
    this.num_cols = 4
    this.hidden_label_id_list = []
    this.history = null
  }

}

export class ImageAnnotationUIContext {
  show_context_menu: boolean
  zoom_value: number
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
  save_warning: object
  annotations_loading: boolean
  any_frame_saving: boolean
  save_loading_frames_list: object[]
  go_to_keyframe_loading: boolean
  save_multiple_frames_error: object
  container_width: number
  container_height: number

  has_changed: boolean
  save_loading: boolean
  has_pending_frames: boolean
  unsaved_frames: number[]
  video_global_attribute_changed: boolean
  video_parent_file_instance_list: Instance[]

  get_userscript: Function

  constructor() {
    this.show_context_menu = false
    this.zoom_value = 1
    this.any_frame_saving = false
    this.save_loading_frames_list = []
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
    this.save_warning = {}
    this.annotations_loading = false
    this.go_to_keyframe_loading = false
    this.save_multiple_frames_error = {}
    this.container_width = 0
    this.container_height = 0
    this.has_changed = false
    this.save_loading = false
    this.has_pending_frames = false
    this.video_global_attribute_changed = false
    this.unsaved_frames = []
    this.video_parent_file_instance_list = []
  }

}


export class SensorFusion3DAnnotationUIContext {
  has_changed: boolean
  container_width: number
  container_height: number
  label_settings: ImageLabelSettings

  get_userscript: Function

  constructor() {
    this.container_width = 0
    this.container_height = 0
    this.label_settings = createDefaultLabelSettings()
  }

}

export class GeoAnnotationUIContext {
  has_changed: boolean
  container_width: number
  container_height: number

  get_userscript: Function

  constructor() {
    this.container_width = 0
    this.container_height = 0
  }

}

export class TextAnnotationUIContext {
  rendering: boolean
  resizing: boolean
  has_changed: boolean
  save_loading: boolean
  container_width: number
  container_height: number

  get_userscript: Function

  bulk_mode: boolean
  search_mode: boolean

  context_menu: any
  current_instance: any
  hover_instance: any

  file: any

  constructor(file) {
    this.container_width = 0
    this.container_height = 0
    this.has_changed = false
    this.save_loading = false
    this.bulk_mode = false
    this.search_mode = false
    this.current_instance = null
    this.hover_instance = null
    this.context_menu = null

    this.rendering = true
    this.resizing = false

    this.file = file
  }

}

export class AudioAnnotationUIContext {
  has_changed: boolean
  container_width: number
  container_height: number

  get_userscript: Function

  constructor() {
    this.container_width = 0
    this.container_height = 0
    this.has_changed = false
  }

}
