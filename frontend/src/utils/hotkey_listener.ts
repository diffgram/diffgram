import hotkeys, { HotkeysEvent } from 'hotkeys-js'

interface HotkeysOptions {
  keys: string
  scope ?: string
  element ?: HTMLElement
}

type KeysOrOpts = string | HotkeysOptions

type KeyEventHandler = (event: KeyboardEvent, handler: HotkeysEvent) => void
/**
 * `HotkeyListener` - A utility class to manage keyboard hotkeys using the `hotkeys-js` library.
 *
 * Features:
 * - **Scoped Hotkeys**: Allows the definition of hotkeys within specific scopes. This enables modular applications 
 *   to define and manage hotkeys that make sense in their specific context without interference.
 *
 * - **Flexible Unbinding**: Offers the ability to clear hotkeys, either entirely, by a specific scope, or by key combinations, 
 *   providing granular control over the registered hotkeys.
 *
 * Usage:
 *
 * 1. **Initialization**:
 *      - Fetch the listener instance: `const listener = HotkeyListener.getInstance()`.
 *
 * 2. **Hotkey Registration**:
 *      - Register a hotkey that reacts on keyup: `listener.onKeyup('ctrl+b', callback)`.
 *      - For keydown events: `listener.onKeydown('ctrl+b', callback)`.
 *
 * 3. **Scopes**:
 *      - Introduce a new scope: `listener.addScope('myScope')`.
 *      - Note: A hotkey will only trigger if its scope is among the added scopes.
 *
 * 4. **Unbinding**:
 *      - Clear hotkeys for a specific scope and key combination: `listener.clear('myScope', 'ctrl+b')`.
 *      - To clear all for a scope: `listener.clear('myScope')`.
 *      - Clear all registered hotkeys: `listener.clear()`.
 *
 * **Important**: Due to `hotkeys-js` providing a singleton instance, `HotkeyListener` uses the singleton pattern 
 * to ensure a single centralized management point.
 *
 * @class
 */
export class HotkeyListener {
  private static instance: HotkeyListener
  private selectedScopes: string[] = []
  private scopeCallbackRegistry: {
    [scope: string]: { keys: string, callback: (event: KeyboardEvent, handler: HotkeysEvent) => void }[]
  } = {}

  private filters: Array<(event: KeyboardEvent) => boolean>
  private defaultFilter: (event: KeyboardEvent) => boolean

  private constructor() {
    this.defaultFilter = hotkeys.filter
    this.filters = [this.defaultFilter]
    this.updateHotkeysFilter()
  }

  public static getInstance(): HotkeyListener {
    if (!HotkeyListener.instance) {
      HotkeyListener.instance = new HotkeyListener()
    }
    return HotkeyListener.instance
  }

  private forceOpts(keysOrOpts: KeysOrOpts): HotkeysOptions {
    if (typeof keysOrOpts === 'string') {
      return { keys: keysOrOpts, scope: this.selectedScopes[0] }
    } else {
      return {
        keys: keysOrOpts.keys,
        scope: keysOrOpts.scope || this.selectedScopes[0],
        element: keysOrOpts.element
      }
    }
  }

  private bindKey(type: 'keyup' | 'keydown', keysOrOpts: KeysOrOpts, cb: KeyEventHandler) {
    const { keys, scope, element } = this.forceOpts(keysOrOpts)
    const scopedCallback = (event: KeyboardEvent, handler: HotkeysEvent) => {
      if (this.selectedScopes.includes(scope)) {
        return cb(event, handler)
      }
    }

    if ( type === 'keyup' ) {
      hotkeys(keys, { scope: 'all', element, keyup: true, keydown: false }, scopedCallback)
    } else { // keydown
      hotkeys(keys, { scope: 'all', element, keyup: false, keydown: true }, scopedCallback)
    }


    if (!this.scopeCallbackRegistry[scope]) {
      this.scopeCallbackRegistry[scope] = []
    }
    this.scopeCallbackRegistry[scope].push({ keys, callback: scopedCallback })
  }

  onKeyup(keysOrOpts: KeysOrOpts, cb: KeyEventHandler) {
    this.bindKey('keyup', keysOrOpts, cb)
  }

  onKeydown(keysOrOpts: KeysOrOpts, cb: KeyEventHandler) {
    this.bindKey('keydown', keysOrOpts, cb)
  }

  addScope(scope: string) {
    if (!this.selectedScopes.includes(scope)) {
      this.selectedScopes.push(scope)
    }
  }

  removeScope(scope: string) {
    const index = this.selectedScopes.indexOf(scope)
    if (index > -1) {
      this.selectedScopes.splice(index, 1)
    }
  }

  clear(scope?: string, keys?: string | string[]) {
    // If neither scope nor keys are provided, clear all hotkeys
    if (!scope && !keys) {
      hotkeys.unbind()
      this.scopeCallbackRegistry = {} // Reset the registry
      return
    }

    // If only scope is provided, clear all hotkeys for that scope
    if (scope && !keys) {
      if (this.scopeCallbackRegistry[scope]) {
        for (const callback of this.scopeCallbackRegistry[scope]) {
          hotkeys.unbind(callback.keys, callback.callback)
        }
        delete this.scopeCallbackRegistry[scope]
      }
      return;
    }

    // If both scope and keys are provided, clear specific hotkeys within that scope
    if (scope && keys) {
      // Convert keys to array if it's a single string
      if (typeof keys === 'string') {
        keys = [keys]
      }

      // Filter callbacks for the specific scope and keys
      const callbacksToRemove =
        this.scopeCallbackRegistry[scope] && this.scopeCallbackRegistry[scope].filter(callback => keys.includes(callback.keys))

      if (callbacksToRemove) {
        callbacksToRemove.forEach(callback => {
          hotkeys.unbind(callback.keys, callback.callback)
        });
      }
    }
  }

  deleteScope(scope: string) {
    this.clear(scope)
    if (this.scopeCallbackRegistry[scope]) {
      delete this.scopeCallbackRegistry[scope]
    }

    this.removeScope(scope)
  }

  /**
   * Add a filter. The filter should return `true` if the event should be processed, and `false` otherwise.
   * @param filter - The filter function to add.
   */
  addFilter(filter: (event: KeyboardEvent) => boolean) {
    this.filters.push(filter)
    this.updateHotkeysFilter()
  }

  /**
   * Remove a filter.
   * @param filter - The filter function to remove.
   */
  removeFilter(filter: (event: KeyboardEvent) => boolean) {
    const index = this.filters.indexOf(filter)
    if (index !== -1) {
      this.filters.splice(index, 1)
    }
    this.updateHotkeysFilter()
  }

  /**
   * Clear all filters
   */
  clearFilters() {
    this.filters = []
    this.updateHotkeysFilter()
  }

  /**
   * Restore the default hotkeys-js filters and remove all the other filters
   */
  restoreDefaultFilters() {
    this.filters = [this.defaultFilter]
    this.updateHotkeysFilter()
  }

  /**
   * This internal method sets the hotkeys filter based on the current list of filters.
   */
  private updateHotkeysFilter() {
    hotkeys.filter = (event: KeyboardEvent) => {
      for (const filter of this.filters) {
        if (!filter(event)) {
          return false
        }
      }
      return true
    }
  }

}
