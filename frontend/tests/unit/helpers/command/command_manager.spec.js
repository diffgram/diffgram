import CommandManager from "../../../../src/helpers/command/command_manager";
import TestCommand from "../TestCalsses/TestCommand";
import TestHistory from "../TestCalsses/TestHistory"

describe("Testing CommandManager class", () => {
    let command_manager;
    let test_command;
    let mockPop;
    let mockRepush;

    const mockPush = jest.fn();
    const mockExecte = jest.fn();
    const mockUndo = jest.fn();

    beforeEach(() => {
        test_command = new TestCommand("One", mockExecte, mockUndo);
        mockPop = jest.fn(() => test_command)
        mockRepush = jest.fn(() => test_command)
        
        const test_history = new TestHistory(mockPush, mockPop, mockRepush);
        command_manager = new CommandManager(test_history);
    })

    it("Tests executeCommand", () => {
        command_manager.executeCommand(test_command)
        expect(mockPush).toHaveBeenCalled();
        expect(mockExecte).toHaveBeenCalled();
    })

    it("Tests undo command", () => {
        command_manager.executeCommand(test_command);
        command_manager.undo();

        expect(mockPop).toHaveBeenCalled();
    })

    it("Tests redo command", () => {
        command_manager.executeCommand(test_command);
        command_manager.undo();
        command_manager.redo();

        expect(mockRepush).toHaveBeenCalled();
    })
})