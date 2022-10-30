import { CommandManager } from "./CommandManager";
import { File } from "./files";
import { Instance } from "./instance";
import { Task } from "./tasks";

export type InstanceStore = {
  instance_list: Array<Instance>
  context: "file" | "task"
  command: CommandManager
  file?: File
  task?: Task
}