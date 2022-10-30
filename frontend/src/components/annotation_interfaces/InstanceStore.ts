import { InstanceStore as InstanceStoreType } from "../../types/InstanceStore"
import { File } from "../../types/files"
import { Instance } from "../../types/instance"
import { Task } from "../../types/tasks"
import { CommandManager as CommandManagerType } from "../../types/CommandManager";
import CommandManager from "../../helpers/command/command_manager";
import History from "../../helpers/history"

export class InstanceStore implements InstanceStoreType {
  private instance_list_private: Instance[];
  public context_private: "file" | "task";
  private file_private: File;
  private task_private: Task;
  private save_status_private: "saved" | "changed" | "saving";
  private command: CommandManagerType;

  get instance_list(): Instance[] {
    return this.instance_list_private
  }

  get context(): "file" | "task" {
    return this.context
  }

  get save_status():  "saved" | "changed" | "saving" {
    return this.save_status_private
  }

  get annotation_item(): File | Task {
    if (this.context === 'file') return this.file_private
    else return this.task_private
  }

  get undo_possible(): boolean {
    return this.command.undo_possible
  }

  get redo_possible(): boolean {
    return this.command.redo_possible
  }

  constructor(
    annotation_item: File | Task,
    instance_list: Instance[] = []
  ) {
    this.instance_list_private = instance_list

    const history = new History()
    this.command = new CommandManager(history)

    if (this.isTask(annotation_item)) {
      this.context_private = "task"
      this.task_private = annotation_item
    } else {
      this.context_private = "file"
      this.file_private = annotation_item
    }
  }

  private isTask(annotation_item: File | Task): annotation_item is Task {
    return (annotation_item as Task).job !== undefined
  }

  public save(): void {}

  public create: (instance_list: Instance[]) => {};

  public delete: (instance_list: Instance[]) => {};

  public update: (instance_list: Instance[]) => {};

  public undo: () => void;
  
  public redo: () => void;
}