import {Instance} from "../instances/Instance";
import InstanceStore from "../helpers/InstanceStore";
import {File} from "../files/File";
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'
import 'vuetify/styles'
import {APICredentials} from "../credentials/APICredentials";
import {DiffgramAPI, NewDiffgramAPI} from "../diffgramAPI/DiffgramAPI";
import {ComponentPublicInstance} from "vue";
import {Directory} from "../files/Directory";
import {LabelSchema} from "../labels/LabelSchema";
export class DiffgramUIBase {
  private instanceStore: InstanceStore;
  private file: File

  private iFrame: HTMLIFrameElement

  private rootComponent: ComponentPublicInstance

  private API: DiffgramAPI

  private directory: Directory

  private schema: LabelSchema

  constructor(root: ComponentPublicInstance,
              iFrame: HTMLIFrameElement,
              credentials: APICredentials,
              hostURL: string,
              schema_id?: number,
              directory_id?: number) {
    this.rootComponent = root
    this.iFrame = iFrame
    this.API = NewDiffgramAPI(hostURL, credentials)
    this.initialize_schema(schema_id)
    this.initialize_directory(directory_id)
  }

  public async initialize_directory(directory_id?: number){
    if(directory_id){
      this.di
      return
    }
    let [response_data, err] = await this.API.Directories.listDirectories(10)
    if (err){
      throw err
    }
    if (response_data?.default_directory){
      this.directory = response_data.default_directory
    }

  }
  public initialize_schema(schema_id?: number){

  }
  public getInstanceList(): Instance[]{
    if(!this.file){
      return []
    }
    let res = this.instanceStore.get_instance_list(this.file.id)
    if (!res){
      return []
    }
    return res
  }

}
