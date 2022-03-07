import { Instance } from "../../components/vue_canvas/instances/Instance"
import { TextAnnotationInstance, TextRelationInstance } from "../../components/vue_canvas/instances/TextInstance";
import InstanceList from "../instance_list";

export abstract class Command {   
    protected instances: Array<Instance>;
    protected instance_list: InstanceList;
    protected replacement_indexes: Array<number> = [];

    constructor(updated_instances: Array<Instance>, instance_list: InstanceList) {
        this.instances = updated_instances.map(inst => {
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

export class CreateInstanceCommand extends Command {
    execute() {
        const id_list = this.get_instances_ids()
        this.instance_list.get_all().forEach((existing_instance, index, array_of_instances) => {
            const { id, creation_ref_id } = existing_instance.get_instance_data()
            if (id_list.includes(id) || id_list.includes(creation_ref_id)) {
                array_of_instances[index].soft_delete = false
            }
        });

        this.instances.forEach((_, index, array_of_instances) => {
            array_of_instances[index].soft_delete = false
        })
    }

    undo() {
        const id_list = this.get_instances_ids()
        this.instance_list.get().forEach((existing_instance, index, array_of_instances) => {
            const { id, creation_ref_id } = existing_instance.get_instance_data()
            if (id_list.includes(id) || id_list.includes(creation_ref_id)) {
                array_of_instances[index].soft_delete = true
            }
        });
    };
}

export class UpdateInstanceCommand extends Command {
    private initial_instances: Array<Instance>;

    public set_initial_instances(initial_instances: Array<Instance>): void {
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

export class DeleteInstanceCommand extends Command {
    execute() {
        console.log("executing delete")
        this.instances.map((instance, index) => {
            instance.soft_delete = true;
            this.instance_list.replace(instance, this.replacement_indexes[index])
        })
    }

    undo() {
        console.log("undo delete")
        this.instances.map((instance, index) => {
            instance.soft_delete = false;
            this.instance_list.replace(instance, this.replacement_indexes[index])
        })
    }
}