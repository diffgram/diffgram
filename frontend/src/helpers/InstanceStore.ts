import Vue from 'vue'
import {Instance} from "../components/vue_canvas/instances/Instance";
export default class InstanceStore {
  private _file_type: any = {};
  private instance_store: any = {};
  private global_instance_store: {[id: number]: Instance} = {};

  public get_global_instance(file_id: number){
    const file_type = this.get_file_type(file_id)
    return this.global_instance_store[file_id]
  }
  public set_global_instance(file_id: number, global_instance: Instance){
    return this.global_instance_store[file_id] =  global_instance
  }
  clear_unsaved(file_id: number): any[] {
    this.instance_store[file_id] = this.instance_store[file_id].filter((instance: any) => instance.id)

    return this.instance_store[file_id]
  }

  get_file_type(file_id: number): string {
    return this._file_type[file_id]
  }

  set_file_type(file_id: number, type: string) {
    this._file_type[file_id] = type
  }

  get_instance_list(file_id: number, frame: number | undefined = undefined): any[] | undefined {
    const file_type = this.get_file_type(file_id)
    if (file_type === "video" && frame !== undefined) return this.instance_store[file_id][frame]

    return this.instance_store[file_id]
  }

  set_instance_list(file_id: number, instance_list: any[]): void {
    this.instance_store[file_id] = instance_list
    Vue.set(this.instance_store, file_id, instance_list)
  }

  // directional idea for organizing instance list better
  /*
  set_instance(
    initialized_instance_list: any[],
    creation_ref: string,
    key: any,
    value: any): void {

    let instance = initialized_instance_list.find(elm => elm.creation_ref === creation_ref);
    let index = initialized_instance_list.indexOf(instance)
    initialized_instance_list[index].value = value 
  }
  */

}
