import Command from "./command"

export default class CommandHistory {
    private history: Array<Command>

    push(command: Command) {
        this.history.push(command)
    }
    pop(): Command {
        return this.history.pop()
    }
}