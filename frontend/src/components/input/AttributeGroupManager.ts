import {v4 as uuidv4} from 'uuid'

export default class AttributeGroupManager {

  public constructor() {

  }

  private are_label_list_equal(list_1, list_2) {
    let labels_1 = []
    let labels_2 = []
    if(list_1){
      labels_1 = list_1
    }
    if(list_2){
      labels_2 = list_2
    }

    const names_list_1 = labels_1.map(l_file => l_file.label.name);
    const names_list_2 = labels_2.map(l_file => l_file.label.name);

    for(const name of names_list_1){
      if(!names_list_2.includes(name)){
        return false
      }
    }
    return true
  }

  public are_attribute_lists_equal(attr_obj_1, attr_obj_2){
    if(!attr_obj_1.attribute_template_list && !attr_obj_2.attribute_template_list){
      return true
    }
    // Get only non archived attribute names.
    let list1 = []
    let list2 = []

    if(attr_obj_1.attribute_template_list){
      list1 = attr_obj_1.attribute_template_list.filter(attr => !attr.archived).map(attr => attr.name);
    }
    if(attr_obj_2.attribute_template_list){
      list2 = attr_obj_2.attribute_template_list.filter(attr => !attr.archived).map(attr => attr.name);
    }

    if(list1.length != list2.length){
      return false
    }

    for(const name of list1){
      if(!list2.includes(name)){
        return false
      }
    }
    return true

  }

  public attributes_groups_are_equal(attr_obj_1, attr_obj_2) {
    /*
    * Returns true if attributes match on all aspects except ID.
    * Useful in context of export uploads.
    * */
    console.log('COMPARING', attr_obj_1, attr_obj_2)
    // Check names are equal.
    if (attr_obj_1.name !== attr_obj_2.name) {
      console.log('NAME NOT EQUAL', attr_obj_1)
      return false
    }
    // Check kind is equal.
    if (attr_obj_2.kind !== attr_obj_2.kind) {
      console.log('kind NOT EQUAL', attr_obj_1)
      return false
    }
    // Check prompt is equal.
    if (attr_obj_1.prompt !== attr_obj_2.prompt) {
      console.log('prompt NOT EQUAL', attr_obj_1)
      return false
    }

    // Check labels
    if(!this.are_label_list_equal(attr_obj_1.label_file_list, attr_obj_2.label_file_list)){
      console.log('are_label_list_equal NOT EQUAL', attr_obj_1)
      return false
    }

    if(!this.are_attribute_lists_equal(attr_obj_1, attr_obj_2)){
      console.log('are_attribute_lists_equal NOT EQUAL', attr_obj_1)
      return false
    }

    // Check default value
    if(attr_obj_1.default_value !== attr_obj_2.default_value){
      console.log('default_value NOT EQUAL', attr_obj_1)
      return false
    }
    // Check default id
    if(attr_obj_1.default_id !== attr_obj_2.default_id){
      console.log('default_id NOT EQUAL', attr_obj_1)
      return false
    }

    // Check min_value
    if(attr_obj_1.min_value !== attr_obj_2.min_value){
      console.log('min_value NOT EQUAL', attr_obj_1)
      return false
    }

    // Check default id
    if(attr_obj_1.max_value !== attr_obj_2.max_value){
      console.log('max_value NOT EQUAL', attr_obj_1)
      return false
    }

    return true

  }

}
