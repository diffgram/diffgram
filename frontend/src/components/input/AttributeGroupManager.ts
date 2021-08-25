import {v4 as uuidv4} from 'uuid'

export default class AttributeGroupManager {

  public constructor() {

  }

  private are_label_list_are_equal(list_1, list_2) {
    const names_list_1 = list_1.map(l_file => l_file.label.name);
    const names_list_2 = list_2.map(l_file => l_file.label.name);

    for(const name of names_list_1){
      if(!names_list_2.includes(name)){
        return false
      }
    }
    return true
  }

  public check_attribute_list_equal(attr_obj_1, attr_obj_2){

    const list1 = attr_obj_1.attribute_template_list;
    const list2 = attr_obj_2.attribute_template_list;

  }

  public attributes_groups_are_equal(attr_obj_1, attr_obj_2) {
    /*
    * Returns true if attributes match on all aspects except ID.
    * Useful in context of export uploads.
    * */

    // Check names are equal.
    if (attr_obj_1.name !== attr_obj_2.name) {
      return false
    }
    // Check kind is equal.
    if (attr_obj_2.kind !== attr_obj_2.kind) {
      return false
    }
    // Check prompt is equal.
    if (attr_obj_1.prompt !== attr_obj_2.prompt) {
      return false
    }

    // Check labels
    if(!this.are_label_list_are_equal(attr_obj_1.label_file_list, attr_obj_2.label_file_list)){
      return false
    }

    // Check default value
    if(attr_obj_1.default_value !== attr_obj_2.default_value){
      return false
    }
    // Check default id
    if(attr_obj_1.default_id !== attr_obj_2.default_id){
      return false
    }


  }

}
