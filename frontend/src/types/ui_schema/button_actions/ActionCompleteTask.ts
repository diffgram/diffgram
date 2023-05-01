
import {AnyAnnotationCtx, BaseAnnotationUIContext} from "../../AnnotationUIContext";
import {CustomButtonWorkflow, AnnotationUIFactory} from "../CustomButtonWorkflow";
import {BaseActionCustomButton} from "../../ui_schema/BaseActionCustomButton";

export class ActionCompleteTask extends BaseActionCustomButton{
  public async execute(annotation_ui_context: BaseAnnotationUIContext, ui_factory_component: AnnotationUIFactory) {
    await ui_factory_component.on_task_annotation_complete_and_save()
  }
}
