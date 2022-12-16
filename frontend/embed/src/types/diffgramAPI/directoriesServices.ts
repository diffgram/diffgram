import {Input} from "../input/Input";
import {APICredentials} from "../credentials/APICredentials";
import {APIConnection, DiffgramAPI, NewDiffgramAPI} from "./DiffgramAPI";
import InstanceList from "../helpers/instance_list";
import {Directory} from "../files/Directory";

export type ListDirectoriesResponse = {
  default_directory: Directory,
  directory_list: Directory[]
}
export class DirectoriesServicesAPIDefinition {
  public baseAPI: APIConnection

  constructor(baseAPI: APIConnection) {
    this.baseAPI = baseAPI
  }

  public async listDirectories(limit: number = 10): Promise<[ListDirectoriesResponse | undefined, any]> {
    let url = `${this.baseAPI.hostUrl}/api/v1/project/${this.baseAPI.credentials.project_string_id}/directory/list`
    try {
      const response = await this.baseAPI.axios.post(url, {limit: limit})
      return [response.data, undefined]
    } catch (err) {
      return [undefined, err]
    }
  }
}
