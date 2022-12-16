import { GlobalAnnotationInstance } from "../instances/GlobalInstance";
import { TextAnnotationInstance, TextRelationInstance } from "../instances/TextInstance";
import { InstanceInterface } from "./interfaces/InstanceData";
import { v4 as uuidv4 } from 'uuid'
import {Instance} from "../instances/Instance";

export default class InstanceList {
    private instance_list: Array<Instance> = [];
    private global_instance: Instance = new GlobalAnnotationInstance();

    constructor(instances?: Array<any>) {
        this.global_instance.type = "global"
        this.global_instance.creation_ref_id = uuidv4();

        if (instances && instances.length > 0) {
            instances.map(instance => {
                let new_instance: TextAnnotationInstance | TextRelationInstance | GlobalAnnotationInstance;
                const { id, label_file, creation_ref_id, attribute_groups } = instance;

                if (instance.type === "text_token") {
                    const { start_token, end_token } = instance
                    new_instance = new TextAnnotationInstance() as TextAnnotationInstance
                    new_instance.create_instance(id, start_token, end_token, label_file, attribute_groups)
                }

                else if (instance.type === "relation") {
                    const { from_instance_id, to_instance_id, soft_delete } = instance
                    new_instance = new TextRelationInstance() as TextRelationInstance
                    new_instance.create_instance(id, from_instance_id, to_instance_id, label_file, attribute_groups, soft_delete)
                }

                else if (instance.type === "global") {
                    const global_instance = new GlobalAnnotationInstance() as GlobalAnnotationInstance
                    global_instance.create_instance(id, creation_ref_id, attribute_groups)
                    this.global_instance = global_instance
                    return
                }

                else return

                new_instance.creation_ref_id = creation_ref_id
                this.instance_list.push(new_instance)
            })
        }
    }

    public set_global_instance(new_global_instance: Instance): void {
        this.global_instance = new_global_instance
    }

    public get(): Array<Instance> {
        const non_deleted = this.instance_list.filter(instance => instance.soft_delete !== true)
        return non_deleted
    }

    public get_global_instance(): Instance {
        return this.global_instance
    }

    public get_all(): Array<Instance> {
        return this.instance_list
    }

    public get_for_save(): Array<Instance> {
        return [...this.instance_list, this.global_instance]
    }

    public push(instances: Array<Instance>) {
        this.instance_list = [... this.instance_list, ... instances]
    }

    public replace(instance: Instance, index: number) {
        this.instance_list.splice(index, 1, instance);
    }
}
