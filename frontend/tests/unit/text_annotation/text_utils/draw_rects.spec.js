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

        expect(rects[0].x).toEqual(tokens[0].start_x)
        expect(rects[0].width).toEqual(tokens[3].start_x + tokens[3].width - tokens[0].start_x)
    })
})