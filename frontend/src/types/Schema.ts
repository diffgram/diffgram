import { LabelColourMap } from "./label_colour_map";
import { LabelFile } from "./label"

export type Schema = {
  id: number
  name: string
  labelColourMap: LabelColourMap
  labelNamesMap: object
  labelList: LabelFile[]
}
