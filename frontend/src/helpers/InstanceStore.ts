export default class InstanceStore {
  private _instance_store: any = {};

  get_instance_list(file_id: number) {
    return this._instance_store[file_id]
  }

  set_instance_list(file_id: number, instance_list: any[]) {
    this._instance_store[file_id] = instance_list
  }
}