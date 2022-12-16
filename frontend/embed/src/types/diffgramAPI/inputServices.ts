import {Input} from "../input/Input";
import {APICredentials} from "../credentials/APICredentials";
import {APIConnection, DiffgramAPI, NewDiffgramAPI} from "./DiffgramAPI";
import InstanceList from "../helpers/instance_list";


export class InputServicesAPIDefinition {
  public baseAPI: APIConnection

  constructor(baseAPI: APIConnection) {
    this.baseAPI = baseAPI
  }

  public async createInputFromURL(file_name: string,
                                  media_url: string,
                                  type: string,
                                  dir_id: number,
                                  instance_list?: InstanceList): Promise<[Input | undefined, any]> {
    let url = `${this.baseAPI.hostUrl}/api/walrus/v1/project/${this.baseAPI.credentials.project_string_id}/input/packet`
    try {

      const inputPacket: Input = {
        media: {
          type: type,
          url: media_url
        },
        type: "from_url",
        directory_id: dir_id,
        original_filename: file_name
      }
      if(instance_list){
        inputPacket.instance_list = instance_list
      }
      const response = await this.baseAPI.axios.post(url, {})
      return [response.data, undefined]
    } catch (err) {
      return [undefined, err]
    }
  }
}
