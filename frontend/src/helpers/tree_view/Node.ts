import { Node } from "../interfaces/TreeNode";
import { v4 as uuidv4 } from "uuid";

export class TreeNode implements Node {
    private id = null;
    private parent_id = null;
    private temp_id: string | null;
    private name: string;

    constructor(name?: string) {
        if (name) {
            this.temp_id = uuidv4()
            this.name = name
        }
    }

    initialize_existing_node(id: number, name: string, parent_id: number) {
        this.id = id;
        this.name = name;
        this.parent_id = parent_id;
    }

    get_id() {
        return this.id || this.temp_id
    }

    get_parent() {
        return this.parent_id
    }

    id_is_set() {
        return typeof this.id === 'number'
    }

    set_id(id: number) {
        this.id = id;
    }

    set_parent(parent_id: number) {
        this.parent_id = parent_id
    }

    update_name(name: string) {
        this.name = name;
    }

    get_render_data() {
        return {
            id: this.get_id(),
            name: this.name,
            parent: this.parent_id,
            children: []
        }
    }
}