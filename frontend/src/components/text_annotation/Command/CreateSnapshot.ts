import { TextInstance } from "./Interfaces"

export class TextInstanceSnapshot {
    private state: TextInstance[];

    constructor (state: TextInstance[]) {
        this.state = state
    }

    get () {
        return this.state
    }
}