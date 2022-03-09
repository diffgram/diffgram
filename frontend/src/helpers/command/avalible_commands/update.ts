import { Command } from "../command"
import { InstanceInterface } from "../../interfaces/InstanceData";

export default class UpdateInstanceCommand extends Command {
    private initial_instances: Array<InstanceInterface>;

    public set_initial_instances(initial_instances: Array<InstanceInterface>): void {
        this.initial_instances = initial_instances.map(instance => this._copyInstance(instance));
    }

    execute() {
        this.instances.map((instance, index) => {
            this.instance_list.replace(instance, this.replacement_indexes[index])
        })
    }

    undo() {
        this.initial_instances.map((instance, index) => {
            this.instance_list.replace(instance, this.replacement_indexes[index])
        })
    }
}