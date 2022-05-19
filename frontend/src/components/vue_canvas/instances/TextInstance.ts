import { Instance } from "./Instance";
import { v4 as uuidv4 } from 'uuid'
import {
  TextInstanceData,
  InstanceInterface,
  TextRelationInstanceData
} from "../../../helpers/interfaces/InstanceData";


export class TextAnnotationInstance extends Instance implements InstanceInterface {
    public start_token: string = null;
    public end_token: string = null;
    public initialized: boolean = true;
    public text_tokenizer: string = "nltk";

    constructor() {
        super();
    }

    public create_instance(id, start_token, end_token, label_file, attribute_groups, soft_delete = false): void {
        this.id = id;
        this.type = "text_token";
        this.creation_ref_id = uuidv4();
        this.start_token = start_token;
        this.end_token = end_token;
        this.label_file = label_file;
        this.label_file_id = label_file.id;
        this.soft_delete = soft_delete;
        this.attribute_groups = attribute_groups;
    }

    public create_frontend_instance(start_token, end_token, label_file, soft_delete = false): void {
        this.type = "text_token";
        this.creation_ref_id = uuidv4();
        this.start_token = start_token;
        this.end_token = end_token;
        this.label_file = label_file;
        this.label_file_id = label_file.id;
        this.soft_delete = soft_delete;
    }

    public update_instance_start_token(start_token): void {
        this.start_token = start_token;
    }

    public update_instance_end_token(end_token): void {
        this.end_token = end_token;
    }

    public get_instance_data(): TextInstanceData {
        const payload: any = {
            id: this.id || this.creation_ref_id,
            type: this.type,
            selected: this.selected,
            start_token: this.start_token,
            end_token: this.end_token,
            label_file: this.label_file,
            label_file_id: this.label_file_id,
            soft_delete: this.soft_delete,
            creation_ref_id: this.creation_ref_id,
            text_tokenizer: this.text_tokenizer,
            attribute_groups: this.attribute_groups
        }
        return payload
    }
}

export class TextRelationInstance extends Instance  implements InstanceInterface{
    public from_instance_id: number = null;
    public to_instance_id: number = null;
    public initialized: boolean = true;
    public text_tokenizer: string = "nltk";
    public from_creation_ref: string;
    public to_creation_ref: string;

    constructor() {
        super();
    }

    public create_instance(id, start_instance, end_instance, label_file, attribute_groups, soft_delete = false): void {
        this.id = id;
        this.type = "relation";
        this.creation_ref_id = uuidv4();
        this.label_file = label_file;
        this.label_file_id = label_file.id;
        this.soft_delete = soft_delete;
        this.attribute_groups = attribute_groups;

        if (typeof start_instance === 'number') this.from_instance_id = start_instance;
        else this.from_creation_ref = start_instance;

        if (typeof end_instance === 'number') this.to_instance_id = end_instance;
        else this.to_creation_ref = end_instance;
    }

    public create_frontend_instance(start_instance, end_instance, label_file, soft_delete = false): void {
        this.type = "relation";
        this.creation_ref_id = uuidv4();
        this.label_file = label_file;
        this.label_file_id = label_file.id;
        this.soft_delete = soft_delete;

        if (typeof start_instance === 'number') this.from_instance_id = start_instance;
        else this.from_creation_ref = start_instance;

        if (typeof end_instance === 'number') this.to_instance_id = end_instance;
        else this.to_creation_ref = end_instance;
    }

    public get_instance_data(): TextRelationInstanceData {
        const payload: any = {
            id: this.id || this.creation_ref_id,
            type: this.type,
            selected: this.selected,
            from_instance_id: this.from_instance_id || this.from_creation_ref,
            to_instance_id: this.to_instance_id || this.to_creation_ref,
            label_file: this.label_file,
            label_file_id: this.label_file_id,
            soft_delete: this.soft_delete,
            creation_ref_id: this.creation_ref_id,
            text_tokenizer: this.text_tokenizer,
            attribute_groups: this.attribute_groups
        }

        return payload
    }
}
