import { LabelColourMap } from "./label_colour_map";
import { LabelFile } from "./label"

export class Schema {
  id: number = null
  name: string = null
  labelColourMap: LabelColourMap = null
  labelNamesMap: object = null
  labelList: LabelFile[] = null
}
