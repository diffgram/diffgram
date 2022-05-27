import { InstanceInterface } from "../../interfaces/InstanceData";
import { Command } from "../command";

export default class UpdateInstanceAttributeCommand extends Command {
    private attribute_groups: any;
    private initial_instances: Array<InstanceInterface> = [];

    public set_new_attribute(key: any, attribute_group: any): void {
        this.attribute_groups = {...this.attribute_groups, [key]: attribute_group};
    }

    execute() {
        if (this.initial_instances.length === 0) this.initial_instances = this.instances.map(inst => this._copyInstance(inst))

        this.instances.forEach((_, index, instanceArray) => {
            instanceArray[index].attribute_groups = { ...instanceArray[index].attribute_groups, ...this.attribute_groups }
        })

        this.instances.map((instance, index) => {
            this.instance_list.replace(instance, this.replacement_indexes[index])
        })
    }

    undo() {
        this.initial_instances.map((instance, index) => {
            const instance_to_modify = this.instance_list.get_all()[this.replacement_indexes[index]]
            instance_to_modify.attribute_groups = {...instance.attribute_groups}
        })
    }
}