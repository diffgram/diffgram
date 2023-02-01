import {Instance} from "./Instance";
import {v4 as uuidv4} from 'uuid'
import {InstanceInterface} from "../../../helpers/interfaces/InstanceData";


export class GlobalInstance extends Instance implements InstanceInterface {
  constructor() {
    super();
    this.type = 'global';
    this.creation_ref_id = uuidv4();
  }

  public create_instance(id, creation_ref_id, attribute_groups): void {
    this.id = id;
    this.type = "global";
    this.creation_ref_id = creation_ref_id;
    this.attribute_groups = attribute_groups;
  }

  create_frontend_instance(attribute_groups): void {
    this.type = "global";
    this.creation_ref_id = uuidv4();
    this.attribute_groups = attribute_groups;
  }

  public get_instance_data(): any {
    let data = super.get_instance_data()
    const payload: any = {
      ...data,
      id: this.id || this.creation_ref_id,
      type: this.type,
      creation_ref_id: this.creation_ref_id,
      attribute_groups: this.attribute_groups,
    }
    return payload
  }

}
