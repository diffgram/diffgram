export interface CommandInterface {
    execute: () => (void);
    undo: () => (void);
}
