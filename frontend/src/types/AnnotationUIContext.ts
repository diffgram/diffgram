import {isBoolean} from "lodash";


export class BaseAnnotationUIContext {
  working_file: File
}

export class ImageAnnotationUIContext extends BaseAnnotationUIContext{
  show_context_menu: boolean
}
