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
})