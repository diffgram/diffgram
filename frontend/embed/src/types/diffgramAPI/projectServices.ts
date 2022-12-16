import {APIConnection} from "./DiffgramAPI";
import InstanceList from "../helpers/instance_list";
import {Input} from "../input/Input";


export class ProjectServicesAPIDefinition {
  public baseAPI: APIConnection

  constructor(baseAPI: APIConnection) {
    this.baseAPI = baseAPI
  }
}
