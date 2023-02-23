import {LabelFile} from "../label";

export type AttributeTemplateGroup = {
  attribute_template_list: Array<any>
  label_file_list: LabelFile[]
  default_id: number
  default_value: string | Array<string>
  global_type: string
  id: number
  ordinal: number
  is_global: boolean
  is_root: boolean

  is_read_only: boolean
  kind: string
  max_value: number
  min_value: number
  name: string
  prompt: string
  show_prompt: string
  time_updated: Date
}
