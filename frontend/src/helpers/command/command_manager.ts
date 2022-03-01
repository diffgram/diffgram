import { Command } from "./command";
import CommandHistory from "./history";


export default class CommandManager {
    private command_history: CommandHistory = new CommandHistory()
    private command_index: number = -1;

    public executeCommand(command: Command) {
        command.execute()
        this.command_history.push(command)
        this.command_index = this.command_index + 1
    }

    public undo() {
        if (this.command_index === -1) return;
        const command_to_undo = this.command_history[this.command_index]
        command_to_undo
    }
    
    public redo() {}
}