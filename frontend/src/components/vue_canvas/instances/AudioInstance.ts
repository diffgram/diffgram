import { Instance } from "./Instance";
import { v4 as uuidv4 } from 'uuid'
import { InstanceInterface } from "../../../helpers/interfaces/InstanceData";


export class AudioAnnotationInstance extends Instance implements InstanceInterface {
    public start_time: string = null;
    public end_time: string = null;
    public initialized: boolean = true;
    public audiosurfer_id: string = null;

    constructor() {
        super();
    }

    public create_instance(id, start_time, end_time, label_file, attribute_groups, soft_delete = false): void {
        this.id = id;
        this.type = "audio";
        this.creation_ref_id = uuidv4();
        this.start_time = start_time;
        this.end_time = end_time;
        this.label_file = label_file;
        this.label_file_id = label_file.id;
        this.soft_delete = soft_delete;
        this.attribute_groups = attribute_groups;
    }

    create_frontend_instance(audiosurfer_id, start_time, end_time, label_file, soft_delete = false): void {
        this.type = "audio";
        this.audiosurfer_id = audiosurfer_id;
        this.creation_ref_id = uuidv4();
        this.start_time = start_time;
        this.end_time = end_time;
        this.label_file = label_file;
        this.label_file_id = label_file.id;
        this.soft_delete = soft_delete;
    }

    public update_instance_start_time(start_time): void {
        this.start_time = start_time;
    }

    public update_instance_end_time(end_time): void {
        this.end_time = end_time;
    }

    public get_instance_data(): any {
        const payload: any = {
            id: this.id || this.creation_ref_id,
            type: this.type,
            selected: this.selected,
            start_time: this.start_time,
            end_time: this.end_time,
            label_file: this.label_file,
            label_file_id: this.label_file_id,
            soft_delete: this.soft_delete,
            creation_ref_id: this.creation_ref_id,
            attribute_groups: this.attribute_groups,
            audiosurfer_id: this.audiosurfer_id
        }
        return payload
    }

}