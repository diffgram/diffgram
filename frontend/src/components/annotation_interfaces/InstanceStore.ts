import { InstanceStore as InstanceStoreType } from "../../types/InstanceStore"
import { File } from "../../types/files"
import { Instance } from "../../types/instance"
import { Task } from "../../types/tasks"
import { CommandManager as CommandManagerType } from "../../types/CommandManager";
import CommandManager from "../../helpers/command/command_manager";
import History from "../../helpers/history"

export class InstanceStore implements InstanceStoreType {
  public instance_list: Instance[];
  public context: "file" | "task";
  public file: File;
  public task: Task;
  public command: CommandManagerType;

  constructor(
    annotation_item: File | Task,
    instance_list: Instance[] = []
  ) {
    this.instance_list = instance_list

    const history = new History()
    this.command = new CommandManager(history)

    if (this.isTask(annotation_item)) {
      this.context = "task"
      this.task = annotation_item
    } else {
      this.context = "file"
      this.file = annotation_item
    }
  }

  private isTask(annotation_item: File | Task): annotation_item is Task {
    return (annotation_item as Task).job !== undefined
  }
}