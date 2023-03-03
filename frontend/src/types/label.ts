import {InstanceColor} from "./instance_color";

export type Label = {
  id: number
  name: string
}

export type LabelFile = {
  ann_is_complete?: boolean
  colour: InstanceColor
  created_time?: Date
  hash?: string
  id: number
  label: Label
  stated?: string
}


export type LabelFileMap ={
  number: LabelFile
}
