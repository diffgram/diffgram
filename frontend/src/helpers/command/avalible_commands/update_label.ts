import { Instance } from "../../../components/vue_canvas/instances/Instance";
import { Command } from "../command";

export default class UpdateInstanceLabelCommand extends Command {
    private label: any;
    private initial_instances: Array<Instance> = [];

    public set_new_label(label: any): void {
        this.label = {...label};
    }

    execute() {
        this.initial_instances = this.instances.map(inst => this._copyInstance(inst))

        this.instances.forEach((_, index, instanceArray) => {
            instanceArray[index].label_file = { ...this.label }
            instanceArray[index].label_file_id = this.label.id
        })

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