import { InstanceInterface } from "../../../../src/helpers/interfaces/InstanceData";

export default class TestInstance implements InstanceInterface {
    public id: number;
    public creation_ref_id: string;
    public type: string;
    public selected: boolean;
    public label_file: any;
    public label_file_id: number;
    public soft_delete: boolean;
    public text_tokenizer: string;
    public attribute_groups: any;

    constructor(id: number, type: string, soft_delete: boolean = false) {
        this.id = id;
        this.type = type;
        this.soft_delete = soft_delete;
    }

    create_instance: () => {};
    create_frontend_instance: () => {};
    get_instance_data: () => {};
}