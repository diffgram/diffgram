export interface Node {
    get_id: Function;
    initialize_existing_node: Function;
    id_is_set: Function;
    set_id: Function;
    set_parent: Function;
    update_name: Function;
    get_render_data: Function;
    get_parent: Function;
}