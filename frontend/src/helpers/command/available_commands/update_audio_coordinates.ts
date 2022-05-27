import { InstanceInterface } from "../../interfaces/InstanceData";
import { Command } from "../command";

export default class UpdateInstanceAudioCoordinatesCommand extends Command {
    private initial_instances: Array<InstanceInterface> = [];
    private start_time: number;
    private end_time: number;

    public set_new_geo_coords(start_time: number, end_time: number): void {
        this.start_time = start_time;
        this.end_time = end_time;
    }

    execute() {
        if (this.initial_instances.length === 0) this.initial_instances = this.instances.map(inst => this._copyInstance(inst))

        this.instances.forEach((_, index, instanceArray) => {
            instanceArray[index]["start_time"] = this.start_time
            instanceArray[index]["end_time"] = this.end_time
        })

        this.instances.map((instance, index) => {
            this.instance_list.replace(instance, this.replacement_indexes[index])
        })
    }

    undo() {
        this.initial_instances.map((instance, index) => {
            const instance_to_modify = this.instance_list.get_all()[this.replacement_indexes[index]]
            instance_to_modify["start_time"] = instance["start_time"]
            instance_to_modify["end_time"] = instance["end_time"]
        })
    }
}