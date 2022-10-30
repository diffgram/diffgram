import { CommandInterface } from "../helpers/interfaces/Command"

export type CommandManager = {
  executeCommand: (executeCommand: CommandInterface) => void
  undo: () => boolean
  redo: () => boolean
  undo_possible: boolean
  redo_possible: boolean
}