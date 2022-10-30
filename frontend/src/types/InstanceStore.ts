import { File } from "./files";
import { Instance } from "./instance";
import { Task } from "./tasks";

export interface InstanceStore {
  annotation_item: File | Task
  instance_list: Array<Instance>
}