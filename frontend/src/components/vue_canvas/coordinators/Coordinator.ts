

export abstract class Coordinator {
  public type: string

  abstract process_mouse_down(): boolean
  abstract process_mouse_up(): boolean
  abstract process_mouse_move(): boolean

}
