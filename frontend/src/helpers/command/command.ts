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

    protected get_insatnces_ids(): Array<any> {
        const id_list = this.instances.map(instance => instance.get_instance_data().id)
        return id_list
    }

    undo() {
        const id_list = this.get_insatnces_ids()
        this.instance_list.get().forEach((existing_instance, index, array_of_instances) => {
            const { id, creation_ref_id} = existing_instance.get_instance_data()
            if (id_list.includes(id) || id_list.includes(creation_ref_id)) {
                array_of_instances[index].soft_delete = true
            }
        });
    }

    abstract execute()
}

export class CreateInstanceCommand extends Command {
    execute() {
        console.log("execute", this.instances)
        this.instances.forEach((_, index, array_of_instances) => {
            array_of_instances[index].soft_delete = false
        })
    }
}