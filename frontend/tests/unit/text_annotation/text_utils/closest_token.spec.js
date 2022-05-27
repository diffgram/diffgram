import closest_token from "../../../../src/components/text_annotation/text_utils/closest_token";
import { tokens, lines } from "../text_test_data"

describe("Closes token search, closest_token.ts", () => {
    it("Should throw error if no arguments supplied", () => {
        try {
            closest_token()
        } catch(e) {
            expect(e).toBeTruthy()
        }
    })

    it("Should throw error if only tokens are supplied", () => {
        try {
            closest_token(tokens)
        } catch(e) {
            expect(e).toBeTruthy()
        }
    })

    it("Should throw error if coordinates are not supplied", () => {
        try {
            closest_token(tokens, lines)
        } catch(e) {
            expect(e).toBeTruthy()
        }
    })

    it("Should not throw error", () => {
        const coordinates = {
            x: 50,
            y: 50
        }
        const token = closest_token(tokens, lines, coordinates)
        expect(token).toBeTruthy()
    })

    it("Should return previous token if x values falls out of token coordinates", () => {
        const test_token = tokens[0]
        const coordinates = {
            x: test_token.start_x + test_token.width + 1,
            y: 5
        }
        const token = closest_token(tokens, lines, coordinates)
        expect(token).toEqual(test_token)
    })

    it("Token should belong to line 0 if the y is 0", () => {
        const test_token = tokens[0]
        const coordinates = {
            x: test_token.start_x + test_token.width - 1,
            y: 0
        }
        const token = closest_token(tokens, lines, coordinates)
        expect(token.line).toEqual(0)
    })

    it("Token should not exist if the line falls of text space", () => {
        const coordinates = {
            x: 50,
            y: 400
        }
        const token = closest_token(tokens, lines, coordinates)
        expect(token).toBeUndefined()
    })
})