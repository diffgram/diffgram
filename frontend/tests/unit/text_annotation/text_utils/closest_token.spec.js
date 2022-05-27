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
})