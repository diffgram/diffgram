import {APICredentials} from "../credentials/APICredentials";
import {ProjectServices, ProjectServicesAPIDefinition} from "./projectServices";
import {CreateInputServices, InputServices, InputServicesAPIDefinition} from "./inputServices";
import axios from 'axios';
import {AxiosInstance} from 'axios';

export type DiffgramAPI = {
  hostUrl: string
  axios: AxiosInstance
  credentials: APICredentials

  // API Services
  Project: ProjectServicesAPIDefinition
  Input: InputServicesAPIDefinition
}


export const NewDiffgramAPI = (hostUrl: string, credentials: APICredentials) => {
  const axiosInstance = axios.create()
  axiosInstance.defaults.headers.common['Authorization'] = credentials.buildAuthHeaderValue();
  const result: DiffgramAPI = {
    hostUrl: hostUrl,
    axios: axiosInstance,
    credentials: credentials,
    Project: ProjectServices,
  }
  let inputAPI = new InputServicesAPIDefinition(result)
}
