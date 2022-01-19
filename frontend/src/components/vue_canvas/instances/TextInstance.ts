import { Instance } from "./Instance";
import { v4 as uuidv4 } from 'uuid'

export class TextAnnotationInstance extends Instance {
    public start_token: string = null;
    public end_token: string = null;
    public initialized: boolean = true;

    constructor() {
        super();
    }

    public create_instance(id, start_token, end_token, label_file): void {
        this.id = id;
        this.type = "text_annotation";
        this.creation_ref_id = uuidv4();
        this.start_token = start_token;
        this.end_token = end_token;
        this.label_file = label_file;
        this.label_file_id = label_file.id;
    }

    public update_instance_start_token(start_token): void {
        this.start_token = start_token;
    }

    public update_instance_end_token(end_token): void {
        this.end_token = end_token;
    }

    public get_instance_data(): object {
        return {
            id: this.id,
            type: this.type,
            selected: this.selected,
            start_token: this.start_token,
            end_token: this.end_token,
            label_file: this.label_file,
            label_file_id: this.label_file_id,
            soft_delete: this.soft_delete,
            creation_ref_id: this.creation_ref_id
        }
    }
}

export class TextRelationInstance extends Instance {
    public from_instance_id: number = null;
    public to_instance_id: number = null;

    constructor() {
        super();
    }

    public create_instance(id, start_instance, end_instance, label_file): void {
        this.id = id;
        this.type = "text_relation";
        this.creation_ref_id = uuidv4();
        this.from_instance_id = start_instance;
        this.to_instance_id = end_instance;
        this.label_file = label_file;
        this.label_file_id = label_file.id;
    }

    public get_instance_data(): object {
        return {
            id: this.id,
            type: this.type,
            selected: this.selected,
            from_instance_id: this.from_instance_id,
            to_instance_id: this.to_instance_id,
            label_file: this.label_file,
            label_file_id: this.label_file_id,
            soft_delete: this.soft_delete,
            creation_ref_id: this.creation_ref_id
        }
    }
}
