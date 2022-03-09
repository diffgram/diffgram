import { CommandInterface } from "../../../../src/helpers/interfaces/Command";

export default class TestCommand implements CommandInterface {
    public test_command_name: string;
    public successfully_executed: boolean;
    public successfully_undone: boolean;

    constructor(test_command_name: string) {
        this.test_command_name = test_command_name;
    }

    execute() {
        this.successfully_executed = true;
    };
    undo() {
        this.successfully_undone = true;
    };
}