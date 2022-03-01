import { Instance } from "../components/vue_canvas/instances/Instance";
import { TextAnnotationInstance, TextRelationInstance } from "../components/vue_canvas/instances/TextInstance";

export default class InstanceList {
    private instance_list: Array<Instance> = [];

    constructor(instances: Array<Object>) {
        if (instances && instances.length > 0) {
            instances.map(instance => {
                if (instance.type === "text_token") {
                    const { id, start_token, end_token, label_file, creation_ref_id } = instance
                    const new_instance = new TextAnnotationInstance()
                    new_instance.create_instance(id, start_token, end_token, label_file)
                    new_instance.creation_ref_id = creation_ref_id
                    this.instance_list.push(new_instance)
                } else {
                    const { id, from_instance_id, to_instance_id, label_file, creation_ref_id, soft_delete } = instance
                    const new_instance = new TextRelationInstance()
                    new_instance.create_instance(id, from_instance_id, to_instance_id, label_file, soft_delete)
                    new_instance.creation_ref_id = creation_ref_id
                    this.instance_list.push(new_instance)
                }
            })
        }
    }
    
    public get(): Array<Instance> {
        const non_deleted = this.instance_list.filter(instance => instance.soft_delete !== true)
        return non_deleted
    }

    public get_all(): Array<Instance> {
        return this.instance_list
    }

    public filter(): Array<Instance> {
        return this.instance_list
    }

    public find(): Instance {
        return this.instance_list[0]
    }

    public push(instances: Array<Instance>) {
        this.instance_list = [... this.instance_list, ... instances]
    }
}