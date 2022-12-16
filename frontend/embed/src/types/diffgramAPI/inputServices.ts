import {Input} from "../input/Input";
import {APICredentials} from "../credentials/APICredentials";
import {DiffgramAPI, NewDiffgramAPI} from "./DiffgramAPI";
import InstanceList from "../helpers/instance_list";


export class InputServicesAPIDefinition {
  public baseAPI: DiffgramAPI

  constructor(baseAPI: DiffgramAPI) {
    this.baseAPI = baseAPI
  }

  public async createInputFromURL(media_url: string, type: string, instance_list?: InstanceList): Promise<[Input | undefined, error]> {
    let url = `${this.baseAPI.hostUrl}/api/walrus/v1/project/${this.baseAPI.credentials.project_string_id}/input/packet`
    try {

      const inputPacket: Input = {
        media: {
          type: type,
          url: media_url
        },
      }
      if(instance_list){
        inputPacket.instance_list = instance_list
      }
      const response = await this.baseAPI.axios.post(url, {})
    } catch (err) {
      return [undefined, err]
    }
  }
}
