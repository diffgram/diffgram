import { Command } from "./command"

export default class CommandHistory {
    private history: Array<Command>
    private undone_history: Array<Command>

    public push(command: Command) {
        this.history.push(command)
    }

    public pop(): Command {
        const command = this.history.pop()
        this.undone_history.push(command)
        return this.history.pop()
    }

    public repush(): Command {
        const repush_command = this.undone_history.pop()
        this.history.push(repush_command)
        return repush_command
    }
}