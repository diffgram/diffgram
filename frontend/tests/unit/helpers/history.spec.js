import CommandHistory from "../../../src/helpers/history";
import TestCommand from "./TestCalsses/TestCommand";

describe("Testing CommandHistory class", () => {
    let history;
    let test_command;

    beforeEach(() => {
        history = new CommandHistory();
        test_command = new TestCommand("Test command");
    })

    it("Undo is not possible if there are no commands in the jistory", () => {
        expect(history.undo_posible).toBeFalsy()
    })

    it("Redo is not possible if there are no commands in the jistory", () => {
        expect(history.redo_posible).toBeFalsy()
    })

    it("Successfully pushes comamnd to the history", () => {
        history.push(test_command)
        expect(history.undo_posible).toBeTruthy()
        expect(history.redo_posible).toBeFalsy()
    })

    it("Successfully undo command", () => {
        history.push(test_command);
        const undone_command = history.pop();
        
        expect(undone_command).toEqual(test_command)
        expect(history.undo_posible).toBeFalsy()
        expect(history.redo_posible).toBeTruthy()
    })

    it("Successfully redo command", () => {
        history.push(test_command);
        history.pop();
        const redone_command = history.repush();
        expect(redone_command).toEqual(test_command)
        expect(history.undo_posible).toBeTruthy()
        expect(history.redo_posible).toBeFalsy()
    })

    it("Return null from undo command if undo is not posible", () => {
        expect(history.undo_posible).toBeFalsy();
        
        const undone_command = history.pop();
        expect(undone_command).toEqual(null);
    })

    it("Return null from redo command if redo is not posible", () => {
        expect(history.redo_posible).toBeFalsy();
        
        const redone_command = history.repush();
        expect(redone_command).toEqual(null);
    })
})