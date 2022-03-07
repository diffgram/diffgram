import { Command } from "../command"

export default class DeleteInstanceCommand extends Command {
    execute() {
        this.instances.map((instance, index) => {
            instance.soft_delete = true;
            this.instance_list.replace(instance, this.replacement_indexes[index])
        })
    }

    undo() {
        this.instances.map((instance, index) => {
            instance.soft_delete = false;
            this.instance_list.replace(instance, this.replacement_indexes[index])
        })
    }
}