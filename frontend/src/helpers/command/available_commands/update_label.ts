import { InstanceInterface } from "../../interfaces/InstanceData";
import { Command } from "../command";

export default class UpdateInstanceLabelCommand extends Command {
    private label: any;
    private initial_instances: Array<InstanceInterface> = [];

    public set_new_label(label: any): void {
        this.label = {...label};
    }

    execute() {
        if (this.initial_instances.length === 0) this.initial_instances = this.instances.map(inst => this._copyInstance(inst))

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
            const instance_to_modify = this.instance_list.get_all()[this.replacement_indexes[index]]
            instance_to_modify.label_file = {...instance.label_file}
            instance_to_modify.label_file_id = instance.label_file.id
        })
    }
}