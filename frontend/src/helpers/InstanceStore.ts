import Vue from 'vue'
export default class InstanceStore {
  private _file_type: any = {};
  private instance_store: any = {};

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
}
