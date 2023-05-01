import {BaseActionCustomButton} from "../BaseActionCustomButton";
import {BaseAnnotationUIContext} from "../../AnnotationUIContext";
import annotation_ui_factory from "../../../components/annotation/annotation_ui_factory.vue";
export type AttributeActionMetadata = {
  attribute_template_id: number
  attribute_value_id: number
  schema_id: number

}
export class ActionSetAttributeValue extends BaseActionCustomButton {

  public async execute(annotation_ui_context: BaseAnnotationUIContext, ui_factory_component: InstanceType<typeof annotation_ui_factory>) {
    const attribute_data = this.metadata as AttributeActionMetadata
    // @ts-ignore
    let sidebar = ui_factory_component.$refs.sidebar_factory.get_current_sidebar_ref();
    if (sidebar && sidebar.$refs.instance_detail_list) {
      sidebar = sidebar.$refs.instance_detail_list
    }
    // Find attribute: only search on global and compound attributes.
    let file_global_attribute = annotation_ui_context.global_attribute_groups_list.find(attr =>
      attr.id === attribute_data.attribute_template_id
    )
    if (file_global_attribute) {
      let attr_ref = sidebar.$refs.global_attributes_list.$refs.attribute_group_list.$refs[`attribute_group_${file_global_attribute.id}`]
      if (!attr_ref) {
        await sidebar.$refs.global_attributes_list.$refs.attribute_group_list.open_panel_for_attribute_id(file_global_attribute.id)
        await ui_factory_component.$nextTick()
        attr_ref = sidebar.$refs.global_attributes_list.$refs.attribute_group_list.$refs[`attribute_group_${file_global_attribute.id}`]
      }
      if (attr_ref && attr_ref.length > 0) {
        attr_ref[0].set_attribute_value(attribute_data.attribute_value_id)
      }
    }
    // TODO: FIND Compound global attribute
  }

}
