import { Command } from "./command/command"

export default class CommandHistory {
    private history: Array<Command> = [];
    private undone_history: Array<Command> = [];

    public undo_posible: Boolean = false;
    public redo_posible: Boolean = false;

    public push(command: Command) {
        this.undone_history = [];
        this.history.push(command)
        this.update_status()
    }

    public pop(): Command {
        if (!this.undo_posible) return;

        const command = this.history.pop()
        this.undone_history.push(command)
        this.update_status()
        return command
    }

    public repush(): Command {
        if (!this.redo_posible) return;

        const command = this.undone_history.pop()
        this.history.push(command)
        this.update_status()
        return command
    }

    private update_status() {
        this.undo_posible = this.history.length > 0;
        this.redo_posible = this.undone_history.length > 0;
    }
}