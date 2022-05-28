import { InstanceInterface } from "../../interfaces/InstanceData";
import { Command } from "../command";

export default class UpdateGlobalAttributeCommand extends Command {
    private attribute_groups: any;
    private initial_instance: InstanceInterface;

    public set_new_attribute(key: any, attribute_group: any): void {
        this.attribute_groups = {...this.attribute_groups, [key]: attribute_group};
    }

    execute() {
        this.initial_instance = this._copyInstance(this.instances[0])
        
        const updated = this.instances[0]
        updated.attribute_groups = { ...this.instances[0].attribute_groups, ...this.attribute_groups }

        this.instance_list.set_global_instance(updated) 
    }

    undo() {
        this.instance_list.set_global_instance(this.initial_instance)
    }
}