import { Command } from "../command"

export default class CreateInstanceCommand extends Command {
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