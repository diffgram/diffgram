import DrawRects from "../../../../src/components/text_annotation/text_utils/draw_rects"
import { tokens, lines, instance_list } from "../text_test_data"

describe("Test DrawRects class (draw_rects.ts)", () => {
    let draw_rects;

    beforeEach(() => {
        draw_rects = new DrawRects(tokens, lines, instance_list)
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