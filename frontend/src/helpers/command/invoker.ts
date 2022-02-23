import CommandHistory from "./history";

class Invoker {
    private history: CommandHistory;

    constructor(){
        this.history = new CommandHistory()
    }

    executeCommand() {}
    undo(){}
    redo(){}
}