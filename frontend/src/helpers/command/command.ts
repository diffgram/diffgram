import { Instance } from "../../components/vue_canvas/instances/Instance"
import { TextAnnotationInstance, TextRelationInstance } from "../../components/vue_canvas/instances/TextInstance";
import InstanceList from "../instance_list";

export abstract class Command {   
    protected instances: Array<Instance>;
    protected instance_list: InstanceList;
    protected replacement_indexes: Array<number> = [];

    constructor(received_instances: Array<Instance>, instance_list: InstanceList) {
        this.instances = received_instances.map(inst => {
            this.replacement_indexes.push(instance_list.get_all().indexOf(inst))
            return this._copyInstance(inst)
        })
        this.instance_list = instance_list
    }

    protected _copyInstance(instance: Instance): Instance {
        let initializedInstance;
        let newInstance = instance.get_instance_data();

        if (instance.type === "text_token") {
            initializedInstance = new TextAnnotationInstance()
        }

        if (instance.type === "relation") {
            initializedInstance = new TextRelationInstance()
        }

        initializedInstance.populate_from_instance_obj(newInstance)
        return initializedInstance;
    };

    protected get_instances_ids(): Array<string | number> {
        const id_list: Array<string | number> = this.instances.map(instance => instance.get_instance_data().id)
        return id_list
    };

    abstract execute(): void;
    abstract undo(): void;
}
