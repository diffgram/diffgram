import { LabelColourMap } from "./label_colour_map";
import { LabelFile } from "./label"

// Represents a Diffgram Label Schema
export class Schema {
  id: number = null
  name: string = null
  labelColourMap: LabelColourMap = null
  labelNamesMap: object = null
  labelList: LabelFile[] = null
  project_id: number
}
