import { debounce } from 'lodash'
import hotkeys, { HotkeysEvent } from 'hotkeys-js'

const DEFAULT_HOTKEYS_OPTIONS = {
  debounceThreshold: 100,
  platformDependent: false,
  preventDefaultEvent: true,
}

export type Platform = 'win' | 'mac' | 'linux'

interface HotkeysOptions {
  keys: string
  scope: string
  element ?: HTMLElement,
  debounceThreshold?: number
  platformDependent?: boolean
  preventDefaultEvent?: boolean
}

export type KeyEventHandler = (event: KeyboardEvent, handler: HotkeysEvent) => void
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
 *      - Register a hotkey that reacts on keyup: `listener.onKeyup({keys: 'ctrl+b', scope: 'foo'}, callback)`.
 *      - For keydown events: `listener.onKeydown({keys: 'ctrl+a,ctrl+b', scope: 'foo'}, callback)`.]
 *      - For binding to individual special keys like shift, ctrl, etc. use onSpecialKeydown and onSpecialKeyup: `listener.onSpecialKeydown('shift', callback)`
 *
 * 3. **Scopes**:
 *      - Select only scopes passed as an argument: `listener.setScopes(['scope_one', 'scope_two'])`.
 *      - Select scope and keep previously selected scopes selected: `listener.addScope('myScope')`.
 *      - Cancle selection of a scope: `listener.removeScope('myScope')`.
 *      - Delete scope and all hotkey bindings: `listener.deleteScope('myScope')`.
 *      - Note: A hotkey will only trigger if its scope is among the selected scopes.
 *
 * 4. **Unbinding**:
 *      - Clear hotkeys for a specific scope and key combination: `listener.clear('myScope', 'ctrl+b')`.
 *      - To clear all for a scope: `listener.clear('myScope')`.
 *      - Clear all registered hotkeys: `listener.clear()`.
 *
 * **Important**: Due to `hotkeys-js` providing a singleton instance, `HotkeyListener` uses the singleton pattern 
 * to ensure a single centralized management point.
 *
  * @example
 * ```javascript
 * const listener = HotkeyListener.getInstance(); // Initialization
 *
 * // Register hotkeys
 * listener.onKeyup({keys: 'ctrl+a', scope: 'foo'}, () => {}); // Register callback to fire when 'ctrl+a' is pressed and scope 'foo' is active
 * listener.onKeyup({keys: 'ctrl+b', scope: 'foo'}, () => {}); // Register callback to fire when 'ctrl+b' is pressed and scope 'foo' is active
 * listener.onKeyup({keys: 'ctrl+c', scope: 'bar'}, () => {}); // Register callback to fire when 'ctrl+c' is pressed and scope 'bar' is active
 *
 * // Enable/disable scopes
 * listener.addScopes('foo'); // Hotkey callbacks registered for 'foo' scope will be active
 * listener.removeScope('foo'); // Hotkey callbacks registered for 'foo' scope won't fire
 * listener.addScopes('bar'); // Hotkey callbacks registered for 'foo' and 'bar' scopes will be active
 * listener.setScopes(['foo']); // Only hotkey callbacks registered for 'foo' scope will be active
 * listener.deleteScope('foo'); // Unselects 'foo' scope and unregisters all the callbacks associated with that scope.

 * listener.addScope('bar'); // Hotkeys for 'bar' scope will still fire callbacks, but not for 'foo' scope since deleteScope was called on it
 * ```
 * TODO:
 * 1. If we are ever in situation where we need to have too many scopes registered
 * at the same time, we can enhance HotkeyListener logic so it unregisters callbacks for non-active scopes.
 * This will reduce the number of active callbacks
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

  private specialKeyState: { [key: string]: boolean } = {
      shift: false,
      control: false,
      alt: false,
      option: false,
      cmd: false,
      command: false,
  };

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

  private bindKey(type: 'keyup' | 'keydown', opts: HotkeysOptions, cb: KeyEventHandler) {
    const {
      keys, scope, element,
      debounceThreshold = DEFAULT_HOTKEYS_OPTIONS.debounceThreshold,
      platformDependent = DEFAULT_HOTKEYS_OPTIONS.platformDependent,
      preventDefaultEvent = DEFAULT_HOTKEYS_OPTIONS.preventDefaultEvent,
    } = opts

    const bindKeys = platformDependent
      ? this.getPlatformBasedKeys(keys)
      : keys

    const scopedCallback = (event: KeyboardEvent, handler: HotkeysEvent) => {
      if (this.selectedScopes.includes(scope)) {
        if (preventDefaultEvent) {
          event.preventDefault()
        }
        return cb(event, handler)
      }
    }

    if ( type === 'keyup' ) {
      hotkeys(bindKeys, { scope: 'all', element, keyup: true, keydown: false }, scopedCallback)
    } else { // keydown
      hotkeys(
        bindKeys,
        { scope: 'all', element, keyup: false, keydown: true },
        debounce(scopedCallback, debounceThreshold, {trailing: false, leading: true}),
      )
    }


    if (!this.scopeCallbackRegistry[scope]) {
      this.scopeCallbackRegistry[scope] = []
    }
    this.scopeCallbackRegistry[scope].push({ keys, callback: scopedCallback })
  }

  onKeyup(opts: HotkeysOptions, cb: KeyEventHandler) {
    this.bindKey('keyup', opts, cb)
  }

  onKeydown(opts: HotkeysOptions, cb: KeyEventHandler) {
    this.bindKey('keydown', opts, cb)
  }

  getScopes() : Array<string> {
    return this.selectedScopes
  }

  setScopes(scopes: Array<string>) : void {
    this.selectedScopes = scopes
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

  toMacStyleHotkeys( keys: string ) : string {
    return keys.replace(/\b(ctrl|control)\b/gi, 'command')
  }

  getPlatform() : Platform {
    const userAgent = window.navigator.userAgent;
    const platform = window.navigator.platform;
    const macosPlatforms = ['Macintosh', 'MacIntel', 'MacPPC', 'Mac68K'];
    let os: Platform = 'win'; // by default assume Windows

    if (macosPlatforms.indexOf(platform) !== -1) {
      os = 'mac';
    } else if (/Linux/.test(platform)) {
      os = 'linux';
    }

    return os;
  }

  // this function asumes that keys argument has windows styles keys (e.g. ctrl)
  private getPlatformBasedKeys( keys: string ) : string {
    const platform = this.getPlatform()

    if (platform === 'mac') {
      return this.toMacStyleHotkeys(keys)
    } else {
      return keys
    }
  }

  private parseSpecialKeyBinding(binding: string) {
    return binding.split(',').map(group => group.split('+').map(key => key.trim()));
  }

  private checkSpecialKeyBindingPressed(bindings: string[][], event: KeyboardEvent): boolean {
    const keyState = {
      shift: hotkeys.shift || event.shiftKey || event.key === 'Shift',
      control: hotkeys.ctrl || event.ctrlKey || event.key === 'Control',
      ctrl: hotkeys.ctrl || event.ctrlKey || event.key === 'Control',
      alt: hotkeys.alt || event.key === 'Alt',
      option: hotkeys.option || event.key === 'Alt',
      cmd: hotkeys.cmd || event.metaKey || event.key === 'Meta',
      command: hotkeys.command || event.metaKey || event.key === 'Meta',
    };

    return bindings.some(group =>
      group.every(key => keyState[key]) // All keys in a group should be pressed
    );
  }

  onSpecialKeydown(opts: HotkeysOptions, cb: KeyEventHandler) {
    const {
      keys, scope, element,
      debounceThreshold = DEFAULT_HOTKEYS_OPTIONS.debounceThreshold,
      platformDependent = DEFAULT_HOTKEYS_OPTIONS.platformDependent,
      preventDefaultEvent = DEFAULT_HOTKEYS_OPTIONS.preventDefaultEvent,
    } = opts


    const bindKeys = platformDependent
      ? this.getPlatformBasedKeys(keys)
     : keys

    const bindings = this.parseSpecialKeyBinding(bindKeys);

    const scopedCallback = (event: KeyboardEvent, handler: HotkeysEvent) => {
      if (!this.selectedScopes.includes(scope) || !this.checkSpecialKeyBindingPressed(bindings, event)) {
        return;
      }

      if (preventDefaultEvent) {
        event.preventDefault();
      }

      cb(event, handler);
    }

    hotkeys(
      '*',
      { element, keyup: false, keydown: true },
      debounce(scopedCallback, debounceThreshold, {trailing: false, leading: true}),
    )
  }


  onSpecialKeyup(opts: HotkeysOptions, cb: KeyEventHandler) {
    const {
      keys, scope, element,
      debounceThreshold = DEFAULT_HOTKEYS_OPTIONS.debounceThreshold,
      platformDependent = DEFAULT_HOTKEYS_OPTIONS.platformDependent,
      preventDefaultEvent = DEFAULT_HOTKEYS_OPTIONS.preventDefaultEvent,
    } = opts


    const bindKeys = platformDependent
      ? this.getPlatformBasedKeys(keys)
      : keys

    const bindings = this.parseSpecialKeyBinding(bindKeys);

    const scopedCallback = (event: KeyboardEvent, handler: HotkeysEvent) => {
      if (!this.selectedScopes.includes(scope) || !this.checkSpecialKeyBindingPressed(bindings, event)) {
        return;
      }

      if (preventDefaultEvent) {
        event.preventDefault();
      }

      cb(event, handler);
    }

    hotkeys(
      '*',
      { element, keyup: true, keydown: false },
      debounce(scopedCallback, debounceThreshold, {trailing: false, leading: true}),
    )
  }


}
