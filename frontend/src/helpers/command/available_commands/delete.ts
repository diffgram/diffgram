import { InstanceInterface } from "../../interfaces/InstanceData";
import { Command } from "../command"

export default class DeleteInstanceCommand extends Command {
    private deleted_relations: Array<number> = [];

    private find_linked_relations(instance: InstanceInterface) {
        const { id } = instance.get_instance_data()
        
        this.instance_list.get_all()
            .map((inst, index) => {
                const { from_instance_id, to_instance_id } = inst.get_instance_data()
                if (
                    inst.type === "relation" && 
                    (id === from_instance_id || id === to_instance_id)
                    && !inst.soft_delete
                ) {
                    inst.soft_delete = true
                    this.deleted_relations.push(index)
                }
            })
    }

    execute() {        
        this.instances.map((instance, index) => {
            instance.soft_delete = true;
            this.find_linked_relations(instance)
            this.instance_list.replace(instance, this.replacement_indexes[index])
        })
    }

    undo() {
        this.instances.map((instance, index) => {
            instance.soft_delete = false;
            this.instance_list.replace(instance, this.replacement_indexes[index])
        })

        const all_instances = this.instance_list.get_all()
        this.deleted_relations.forEach((index) => {
            all_instances[index].soft_delete = false
        });
    }
}