import { CommandInterface } from "../../../../src/helpers/interfaces/Command";

export default class TestCommand implements CommandInterface {
    public name: string;
    private mockExecute: Function;
    private mockUndo: Function;

    constructor(name: string, mockExecute?: Function, mockUndo?: Function) {
        this.name = name;
        this.mockExecute = mockExecute;
        this.mockUndo = mockUndo;
    }

    execute() {
        this.mockExecute()
    };
    
    undo() {
        this.mockUndo()
    };
}