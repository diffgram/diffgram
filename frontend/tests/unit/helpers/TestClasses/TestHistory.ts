import { CommandInterface } from "../../../../src/helpers/interfaces/Command";
import { HistoryInterface } from "../../../../src/helpers/interfaces/History";

export default class TestHistory implements HistoryInterface {
    private mockPush: Function;
    private mockPop: Function;
    private mockRepush: Function;

    constructor(mockPush: Function, mockPop: Function, mockRepush: Function) {
        this.mockPush = mockPush;
        this.mockPop = mockPop;
        this.mockRepush = mockRepush;
    }

    public push() {
        this.mockPush()
    }

    public pop() {
        return this.mockPop()
    }

    public repush() {
        return this.mockRepush()
    }
}