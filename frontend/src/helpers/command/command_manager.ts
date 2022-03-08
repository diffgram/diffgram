import { Command } from "./command";
import CommandHistory from "../history";


export default class CommandManager {
    private command_history: CommandHistory;
    
    constructor(command_history: CommandHistory) {
        this.command_history = command_history;
    }

    public executeCommand(command: Command) {
        command.execute()
        this.command_history.push(command)
    }

    public undo() {
        const command_to_undo = this.command_history.pop()
        command_to_undo.undo()
        return true
    }

    public redo() {
        const command_to_redo = this.command_history.repush()
        command_to_redo.execute()
        return true
    }
}