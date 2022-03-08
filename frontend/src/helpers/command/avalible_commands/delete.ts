import { Instance } from "../../../components/vue_canvas/instances/Instance";
import { Command } from "../command"

export default class DeleteInstanceCommand extends Command {
    private deleted_relations: Array<Instance> = [];
    
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