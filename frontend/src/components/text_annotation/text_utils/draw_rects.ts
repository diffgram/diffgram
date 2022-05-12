import { InstanceData } from "../../../helpers/interfaces/InstanceData";
import InstanceList from "../../../helpers/instance_list"

export default class DrawRects {
    private token_list: Array<any>;
    private line_list: Array<any>;
    private instance_list: InstanceList;

    constructor(
        token_list: Array<any>, 
        line_list: Array<any>,
        instance_list: InstanceList
        ) {
            this.update_render_data(token_list, line_list, instance_list)
    }

    update_render_data(
        token_list: Array<any>, 
        line_list: Array<any>,
        instance_list: InstanceList
        ) {
        this.token_list = token_list;
        this.line_list = line_list;
        this.instance_list = instance_list;
    }

    generate_rects_from_instance(instance: InstanceData) {
        let start_token_id: number;
        let end_token_id: number;

        const { id: instance_id, type: instance_type, start_token, end_token, from_instance_id, to_instance_id, label_file} = instance.get_instance_data()
        const { hex: color } = label_file.colour;

        if (instance_type === "relation") {
            const start_instance = this.instance_list.get().find(find_instance => find_instance.get_instance_data().id === from_instance_id)
            start_token_id = this.token_list.find(token => token.id === start_instance["start_token"]).id
            
            const end_instance = this.instance_list.get().find(find_instance => find_instance.get_instance_data().id === to_instance_id)
            end_token_id = this.token_list.find(token => token.id === end_instance["end_token"]).id
        } else {
            start_token_id = start_token;
            end_token_id = end_token;
        }
        
        const base_rects = this.generate_rects(start_token_id, end_token_id)
        const instance_rects = base_rects.map(rect => ({...rect, instance_id, instance_type, color }))

        return instance_rects
    }

    generate_selection_rect(start_token_id: number, end_token_id: number) {
        const base_rects = this.generate_rects(start_token_id, end_token_id)
        const selection_rects = base_rects.map(rect => ({...rect, start_token_id, end_token_id }))

        return selection_rects
    }

    private generate_rects(
        start_token_id: number, 
        end_token_id: number, 
        ) {
        const rects = [];
        let x: number;
        let y: number;
        let width: number;

        const start_token = this.token_list.find(token => token.id === start_token_id)
        let end_token = this.token_list.find(token => token.id === end_token_id)

        if (!end_token) end_token = start_token

        if (start_token.line === end_token.line) {
            if (start_token_id <= end_token_id) {
                x = start_token.start_x;
                y = this.line_list[start_token.line].y + 3;
                width = end_token.start_x + end_token.width - start_token.start_x;
            } else {
                x = end_token.start_x;
                y = this.line_list[end_token.line].y + 3;
                width = start_token.start_x + start_token.width - end_token.start_x;
            }

            rects.push({ x, y, line: start_token.line, width})
        }

        else if (start_token_id > end_token_id) {
            for (let i = end_token.line; i <= start_token.line; ++i) {
                if (i === start_token.line) {
                    const first_token_in_the_line = this.token_list.find(token => token.line == start_token.line)
                    
                    x = first_token_in_the_line.start_x;
                    y = this.line_list[first_token_in_the_line.line].y + 3;
                    width = start_token.start_x + start_token.width - first_token_in_the_line.start_x;
                  } else if (i === end_token.line) {
                    const last_token_in_the_line = this.token_list.filter(token => token.line == end_token.line)
                    
                    x = end_token.start_x;
                    y = this.line_list[end_token.line].y + 3;
                    width = last_token_in_the_line[last_token_in_the_line.length - 1].start_x + last_token_in_the_line[last_token_in_the_line.length - 1].width - end_token.start_x;
                  } else {
                    const last_token_in_the_line = this.token_list.filter(token => token.line == this.line_list[i].id)
                    const first_token_in_the_line = this.token_list.find(token => token.line == this.line_list[i].id)
                    
                    x = first_token_in_the_line.start_x;
                    y = this.line_list[first_token_in_the_line.line].y + 3;
                    width = last_token_in_the_line[last_token_in_the_line.length - 1].start_x + last_token_in_the_line[last_token_in_the_line.length - 1].width - first_token_in_the_line.start_x;
                }
                rects.push({ x, y, line: i, width })
            }
        } else {
            for (let i = start_token.line; i <= end_token.line; ++i) {
                if (i === start_token.line) {
                    const last_token_in_the_line = this.token_list.filter(token => token.line == start_token.line)

                    x = start_token.start_x;
                    y = this.line_list[start_token.line].y + 3;
                    width = last_token_in_the_line[last_token_in_the_line.length - 1].start_x + last_token_in_the_line[last_token_in_the_line.length - 1].width - start_token.start_x;
                } else if (i === end_token.line) {
                    const first_token_in_the_line = this.token_list.find(token => token.line == end_token.line)

                    x = first_token_in_the_line.start_x;
                    y = this.line_list[first_token_in_the_line.line].y + 3;
                    width = end_token.start_x + end_token.width - first_token_in_the_line.start_x;
                } else {
                    const last_token_in_the_line = this.token_list.filter(token => token.line == this.line_list[i].id)
                    const first_token_in_the_line = this.token_list.find(token => token.line == this.line_list[i].id)

                    x = first_token_in_the_line.start_x;
                    y = this.line_list[first_token_in_the_line.line].y + 3;
                    width = last_token_in_the_line[last_token_in_the_line.length - 1].start_x + last_token_in_the_line[last_token_in_the_line.length - 1].width - first_token_in_the_line.start_x;
                }

                rects.push({ x, y, line: i, width })
            }
        }

        return rects
    }
}