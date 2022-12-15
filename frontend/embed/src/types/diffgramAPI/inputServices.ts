import {Input} from "../input/Input";
import {APICredentials} from "../credentials/APICredentials";
import {DiffgramAPI, NewDiffgramAPI} from "./DiffgramAPI";


export class InputServicesAPIDefinition{
  public baseAPI: DiffgramAPI

  constructor(baseAPI: DiffgramAPI) {
    this.baseAPI = baseAPI
  }

  public async createInputFromURL(): Promise<[Input, error]>{
    let url = `${hostURL}/api/walrus/v1/project/${credentials.project_string_id}/input/packet`

  }
}

export const CreateInputServices = (hostURL: string, credentials: APICredentials): InputServicesAPIDefinition => {
  return {
    createInputFromURL: a
  }
}
