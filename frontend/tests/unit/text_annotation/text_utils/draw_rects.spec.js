import DrawRects from "../../../../src/components/text_annotation/text_utils/draw_rects"
import InstanceList from "../../../../src/helpers/instance_list";
import { TextAnnotationInstance, TextRelationInstance } from "../../../../src/components/vue_canvas/instances/TextInstance";
import { tokens, lines, instance_list } from "../text_test_data"

describe("Test DrawRects class's generate_rects function (draw_rects.ts)", () => {
    let draw_rects;

    beforeEach(() => {
        draw_rects = new DrawRects(tokens, lines, instance_list)
    })

    it("Should return one rect with the start coordinate of token and width of the token if end token is not provided", () => {
        const rects = draw_rects.generate_rects(tokens[0].id, undefined)
        expect(rects[0].x).toEqual(tokens[0].start_x)
        expect(rects[0].width).toEqual(tokens[0].width)
    })

    it("Should return one rect with the start coordinate of token and width of the token is start_token_id === end_token_id", () => {
        const rects = draw_rects.generate_rects(tokens[0].id, tokens[0].id)
        expect(rects[0].x).toEqual(tokens[0].start_x)
        expect(rects[0].width).toEqual(tokens[0].width)
    })

    it("Should return one rect with the start coordinate of start token and width that covers all the selected tokens if the tokens are on the same line (start token < end token)", () => {
        const rects = draw_rects.generate_rects(tokens[0].id, tokens[3].id)

        expect(rects[0].x).toEqual(tokens[0].start_x)
        expect(rects[0].width).toEqual(tokens[3].start_x + tokens[3].width - tokens[0].start_x)
    })

    it("Should return one rect with the start coordinate of end token and width that covers all the selected tokens if the tokens are on the same line (end token < start token)", () => {
        const rects = draw_rects.generate_rects(tokens[3].id, tokens[1].id)

        expect(rects[0].x).toEqual(tokens[1].start_x)
        expect(rects[0].width).toEqual(tokens[3].start_x + tokens[3].width - tokens[1].start_x)
    })

    it("Should return array of rects that cover selection of multiline (start token < end token)", () => {
        const start_token = tokens[2]
        const first_line_last_token = tokens.filter(token => token.line === 0).pop()

        const second_line_tokens = tokens.filter(token => token.line === 1)
        const seond_line_token_count = second_line_tokens.length

        const third_line_start_token = tokens.find(token => token.line === 2)
        const end_token = tokens.filter(token => token.line === 2)[2]

        const rects = draw_rects.generate_rects(start_token.id, end_token.id)

        const start_line_rect = rects[0]
        const mid_line_rect = rects[1]
        const end_line_rect = rects[2]

        expect(start_line_rect.x).toEqual(start_token.start_x)
        expect(start_line_rect.width).toEqual(first_line_last_token.start_x + first_line_last_token.width - start_token.start_x)

        expect(second_line_tokens[0].x).toEqual(mid_line_rect.start_x)
        expect(mid_line_rect.width).toEqual(second_line_tokens[seond_line_token_count - 1].start_x + second_line_tokens[seond_line_token_count - 1].width - second_line_tokens[0].start_x)

        expect(end_line_rect.x).toEqual(third_line_start_token.start_x)
        expect(end_line_rect.width).toEqual(end_token.start_x + end_token.width - third_line_start_token.start_x)
    })

    it("Should return array of rects that cover selection of multiline (start token > end token)", () => {
        const start_token = tokens.filter(token => token.line === 2)[2]
        const end_token = tokens[2]

        const first_line_last_token = tokens.filter(token => token.line === 0).pop()

        const second_line_tokens = tokens.filter(token => token.line === 1)
        const seond_line_token_count = second_line_tokens.length

        const third_line_start_token = tokens.find(token => token.line === 2)

        const rects = draw_rects.generate_rects(start_token.id, end_token.id)

        const start_line_rect = rects[0]
        const mid_line_rect = rects[1]
        const end_line_rect = rects[2]

        expect(start_line_rect.x).toEqual(end_token.start_x)
        expect(start_line_rect.width).toEqual(first_line_last_token.start_x + first_line_last_token.width - end_token.start_x)

        expect(second_line_tokens[0].x).toEqual(mid_line_rect.start_x)
        expect(mid_line_rect.width).toEqual(second_line_tokens[seond_line_token_count - 1].start_x + second_line_tokens[seond_line_token_count - 1].width - second_line_tokens[0].start_x)

        expect(end_line_rect.x).toEqual(third_line_start_token.start_x)
        expect(end_line_rect.width).toEqual(start_token.start_x + start_token.width - third_line_start_token.start_x)
    })
})

describe("Test DrawRects class's generate_selection_rect function (draw_rects.ts)", () => {
    let draw_rects;

    beforeEach(() => {
        draw_rects = new DrawRects(tokens, lines, instance_list)
    })

    it("Should return array of rects with added start_token_id and end_token_id in the array elements", () => {
        const rects = draw_rects.generate_selection_rect(tokens[0].id, tokens[0].id)

        expect(rects[0]).toMatchObject({
            start_token_id: expect.any(Number),
            end_token_id: expect.any(Number)
        })
    })
})

describe("Test DrawRects class's generate_rects_from_instance function (draw_rects.ts)", () => {
    let draw_rects;
    let instance_list;
    let first_text_token_instance;
    let second_text_token_instance;

    const label_file = {
        id: 1,
        colour: {
            hex: '#000'
        }
    }

    beforeEach(() => {
        draw_rects = new DrawRects(tokens, lines, instance_list)
        instance_list = new InstanceList()

        first_text_token_instance = new TextAnnotationInstance()
        first_text_token_instance.create_instance(1, 0, 1, label_file, [])

        second_text_token_instance = new TextAnnotationInstance()
        second_text_token_instance.create_instance(2, 2, 3, label_file, [])

        instance_list.push([first_text_token_instance, second_text_token_instance])
    })

    it("Should return array of rects with added instance_id, instance_type and color in the array elements for text_token instance type", () => {
        const rects = draw_rects.generate_rects_from_instance(first_text_token_instance)
        
        expect(rects[0]).toMatchObject({
            instance_id: expect.any(Number),
            instance_type: expect.any(String),
            color: expect.any(String),
        })
    })

    it("Should return array of rects with added instance_id, instance_type and color in the array elements for text_token instance type", () => {
        const rects = draw_rects.generate_rects_from_instance(first_text_token_instance)
        
        expect(rects[0]).toMatchObject({
            instance_id: expect.any(Number),
            instance_type: expect.any(String),
            color: expect.any(String),
        })
    })

    it("Should return array of rects with added instance_id, instance_type and color in the array elements for relation instance type", () => {
        const first_instance_relation = new TextRelationInstance()
        first_instance_relation.create_frontend_instance(
            first_text_token_instance.get_instance_data().id,
            second_text_token_instance.get_instance_data().id,
            label_file
        )

        instance_list.push([first_instance_relation])

        const rects = draw_rects.generate_rects_from_instance(first_instance_relation)
        
        expect(rects[0]).toMatchObject({
            instance_id: expect.any(String),
            instance_type: expect.any(String),
            color: expect.any(String),
        })
    })
})