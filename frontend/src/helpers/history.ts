import { CommandInterface } from "./interfaces/Command";
import { HistoryInterface } from "./interfaces/History";

export default class CommandHistory implements HistoryInterface {
    private history: Array<CommandInterface> = [];
    private undone_history: Array<CommandInterface> = [];

    public undo_posible: Boolean = false;
    public redo_posible: Boolean = false;

    public push(command: CommandInterface) {
        this.undone_history = [];
        this.history.push(command)
        this.update_status()
    }

    public pop(): CommandInterface {
        if (!this.undo_posible) return null;

        const command = this.history.pop()
        this.undone_history.push(command)
        this.update_status()
        return command
    }

    public repush(): CommandInterface {
        if (!this.redo_posible) return null;

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