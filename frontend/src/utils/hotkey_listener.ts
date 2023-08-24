import hotkeys, {HotkeysEvent} from 'hotkeys-js';

interface HotkeysOptions {
  keys: string
  scope ?: string
  element ?: HTMLElement
}

type KeysOrOpts = string | HotkeysOptions

const GLOBAL_SCOPE: string = 'all'

// NOTE:
// 1. Using command only works with keydown events, not keyup events
export class HotkeyListener {

  private static instance: HotkeyListener

  private static GLOBAL_SCOPE: string = GLOBAL_SCOPE

  private selectedScope: string = GLOBAL_SCOPE

  private origHotkeysFilter: (event: KeyboardEvent) => boolean = hotkeys.filter

  private isAllDisabled: boolean = false

  private constructor() { }

  public static getInstance(): HotkeyListener {
    if (!HotkeyListener.instance) {
      HotkeyListener.instance = new HotkeyListener();
    }

    return HotkeyListener.instance;
  }

  private forceOpts( keysOrOpts: KeysOrOpts ) : HotkeysOptions {
    if (typeof keysOrOpts === 'string') {
      return { keys: keysOrOpts }
    } else {
      return keysOrOpts
    }
  }

  onKeyup( keysOrOpts: KeysOrOpts, cb: (event: any, handler: any ) => void ) {
    const {
      keys, scope = this.selectedScope, element
    } = this.forceOpts(keysOrOpts)
    hotkeys(keys, {scope, element, keyup: true, keydown: false}, cb)
  }

  onKeydown( keysOrOpts: KeysOrOpts, cb: (event: any, handler: any ) => void ) {
    const {
      keys, scope = this.selectedScope, element
    } = this.forceOpts(keysOrOpts)
    hotkeys(keys, {scope, element, keyup: false, keydown: true}, cb)
  }

  setGlobalScope() {
    this.selectedScope = HotkeyListener.GLOBAL_SCOPE
    hotkeys.setScope(HotkeyListener.GLOBAL_SCOPE)
  }

  setScope( scope: string ) : void {
    this.selectedScope = scope
    hotkeys.setScope(scope)
  }

  getScope() : string {
    return this.selectedScope
  }

  deleteScope( scope: string ) {
    if ( this.selectedScope === scope ) {
      this.selectedScope = HotkeyListener.GLOBAL_SCOPE
      hotkeys.setScope(this.selectedScope)
    }
    return hotkeys.deleteScope(scope)
  }

  disableSelectedScope() {
    // setting hotkyes intrenally to global scope,
    // so currently selected scope event handlers do not fire
    hotkeys.setScope(HotkeyListener.GLOBAL_SCOPE)
  }

  enableSelectedScope() {
    hotkeys.setScope(this.selectedScope)
  }

  disableAll() {
    if ( this.isAllDisabled ) {
      return
    }

    hotkeys.filter = () => false

    this.isAllDisabled = true
  }

  enableAll() {
    if ( !this.isAllDisabled ) {
      return
    }

    hotkeys.filter = this.origHotkeysFilter

    this.enableSelectedScope()

    this.isAllDisabled = false
  }

  trigger( keys: string, scope ?: string ) {
    hotkeys.trigger(keys, scope)
  }

  clearAll() {
    hotkeys.unbind()
  }

  getAllKeyCodes() {
    return hotkeys.getAllKeyCodes()
  }
}
