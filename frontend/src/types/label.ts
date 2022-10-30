import {InstanceColor} from "./instance_color";

export type Label = {
  id: number
  name: string
}

export type LabelFile = {
  ann_is_complete: boolean
  colour: InstanceColor
  created_time: Date
  hash: string
  id: number
  label: Label
  stated: string
}

export type LabelSchema = {
  id: number,
  name: string,
  project_id: number,
  member_created_id: number | null,
  member_updated_id: number | null,
  is_default: boolean,
  archived: boolean,
  time_created: string,
  time_updated: string | null
}