import { CommandManager } from "./CommandManager";
import { File } from "./files";
import { Instance } from "./instance";
import { Task } from "./tasks";

export type InstanceStore = {
  instance_list: Array<Instance>
  context: "file" | "task"
  save_status: "saved" | "changed" | "saving"
  undo_possible: boolean
  redo_possible: boolean
  annotation_item: File | Task
  save: () => void
  undo: () => void
  redo: () => void
  create: (instance_list: Instance[]) => void
  delete: (instance_list: Instance[]) => void
  update: (instance_list: Instance[]) => void
}