import { Instance } from "../../components/vue_canvas/instances/Instance"
import { TextAnnotationInstance, TextRelationInstance } from "../../components/vue_canvas/instances/TextInstance";
import InstanceList from "../instance_list";

export abstract class Command {   
    protected instances: Array<Instance>;
    protected instance_list: InstanceList;

    constructor(updated_instances: Array<Instance>, instance_list: InstanceList) {
        this.instances = updated_instances.map(inst => this._copyInstance(inst))
        this.instance_list = instance_list
    }

    private _copyInstance(instance: Instance): Instance {
        if (instance.type === "text_token") {
            let newInstance = instance.get_instance_data();
            let initializedInstance = new TextAnnotationInstance()
            initializedInstance.populate_from_instance_obj(newInstance)
            return initializedInstance;
        }

        if (instance.type === "relation") {
            let newInstance = instance.get_instance_data();
            let initializedInstance = new TextRelationInstance()
            initializedInstance.populate_from_instance_obj(newInstance)
            return initializedInstance;
        }
    }

    undo() {}

    abstract execute()
}

export class CreateInstanceCommand extends Command {
    execute() {
        this.instances.forEach((_, index, array_of_instances) => {
            array_of_instances[index].soft_delete = false
        })
    }
}