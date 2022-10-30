export interface HistoryInterface {
    push: Function;
    pop: Function;
    repush: Function;
    undo_posible: boolean,
    redo_posible: boolean,
}