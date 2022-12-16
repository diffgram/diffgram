import {APICredentials} from "../credentials/APICredentials";
import {ProjectServicesAPIDefinition} from "./projectServices";
import {InputServicesAPIDefinition} from "./inputServices";
import axios from 'axios';
import {AxiosInstance} from 'axios';
import {DirectoriesServicesAPIDefinition} from "./directoriesServices";

export type APIConnection = {
  hostUrl: string
  axios: AxiosInstance
  credentials: APICredentials
}
export type DiffgramAPI = {
  apiConnection: APIConnection

  // API Services
  Project: ProjectServicesAPIDefinition
  Input: InputServicesAPIDefinition
  Directories: DirectoriesServicesAPIDefinition
}


export const NewDiffgramAPI = (hostUrl: string, credentials: APICredentials): DiffgramAPI => {
  const axiosInstance = axios.create()
  axiosInstance.defaults.headers.common['Authorization'] = credentials.buildAuthHeaderValue();
  const conn: APIConnection = {
    hostUrl: hostUrl,
    axios: axiosInstance,
    credentials: credentials,

  }
  const result: DiffgramAPI = {
    apiConnection: conn,
    Input: new InputServicesAPIDefinition(conn),
    Project: new ProjectServicesAPIDefinition(conn),
    Directories: new DirectoriesServicesAPIDefinition(conn),
  }
  return result
}
