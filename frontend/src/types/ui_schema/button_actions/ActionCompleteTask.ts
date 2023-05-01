import {BaseActionCustomButton} from "../BaseActionCustomButton";
import {AnyAnnotationCtx, BaseAnnotationUIContext} from "../../AnnotationUIContext";
import annotation_ui_factory from "../../../components/annotation/annotation_ui_factory.vue";


export class ActionCompleteTask extends BaseActionCustomButton{
  public async execute(annotation_ui_context: BaseAnnotationUIContext, ui_factory_component: InstanceType<typeof annotation_ui_factory>) {
    await ui_factory_component.on_task_annotation_complete_and_save()
  }
}
