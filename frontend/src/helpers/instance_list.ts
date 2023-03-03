import { GlobalInstance } from "../components/vue_canvas/instances/GlobalInstance";
import { TextAnnotationInstance, TextRelationInstance } from "../components/vue_canvas/instances/TextInstance";
import { InstanceInterface } from "./interfaces/InstanceData";
import { v4 as uuidv4 } from 'uuid'

export default class InstanceList {
    private instance_list: Array<InstanceInterface> = [];
    private global_instance: InstanceInterface = new GlobalInstance();

    constructor(instances?: Array<any>) {
        this.global_instance.type = "global"
        this.global_instance.creation_ref_id = uuidv4();

        if (instances && instances.length > 0) {
            instances.map(instance => {
                let new_instance: InstanceInterface;
                const { id, label_file, creation_ref_id, attribute_groups } = instance;

                if (instance.type === "text_token") {
                    const { start_token, end_token } = instance
                    new_instance = new TextAnnotationInstance()
                    new_instance.create_instance(id, start_token, end_token, label_file, attribute_groups)
                }

                else if (instance.type === "relation") {
                    const { from_instance_id, to_instance_id, soft_delete } = instance
                    new_instance = new TextRelationInstance()
                    new_instance.create_instance(id, from_instance_id, to_instance_id, label_file, attribute_groups, soft_delete)
                }

                else if (instance.type === "global") {
                    const global_instance = new GlobalInstance()
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

    public set_global_instance(new_global_instance: InstanceInterface): void {
        this.global_instance = new_global_instance
    }

    public get(): Array<InstanceInterface> {
        const non_deleted = this.instance_list.filter(instance => instance.soft_delete !== true)
        return non_deleted
    }

    public get_global_instance(): InstanceInterface {
        return this.global_instance
    }

    public get_all(): Array<InstanceInterface> {
        return this.instance_list
    }

    public get_for_save(): Array<InstanceInterface> {
        return [...this.instance_list, this.global_instance]
    }

    public push(instances: Array<InstanceInterface>) {
        this.instance_list = [... this.instance_list, ... instances]
    }

    public replace(instance: InstanceInterface, index: number) {
        this.instance_list.splice(index, 1, instance);
    }
}
