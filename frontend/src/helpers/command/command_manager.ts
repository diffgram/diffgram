import { HistoryInterface } from "../interfaces/History";
import { CommandInterface } from "../interfaces/Command";
import { CommandManager as CommandManagerType } from "../../types/CommandManager"

export default class CommandManager implements CommandManagerType {
    private command_history: HistoryInterface;
    
    constructor(command_history: HistoryInterface) {
        this.command_history = command_history;
    }

    get undo_possible(): boolean {
        return this.command_history.undo_posible
    }

    get redo_possible(): boolean {
        return this.command_history.undo_posible
    }

    public executeCommand(command: CommandInterface) {
        command.execute()
        this.command_history.push(command)
    }

    public undo() {
        const command_to_undo = this.command_history.pop();
        command_to_undo.undo();
        return true
    }

    public redo() {
        const command_to_redo = this.command_history.repush()
        command_to_redo.execute()
        return true
    }
}