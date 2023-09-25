import { HotkeyListener } from '../../../src/utils/hotkey_listener';

describe('HotkeyListener', () => {
  let listener
  let testElement

  beforeEach(() => {
    listener = HotkeyListener.getInstance()

    // Create an element to dispatch events on.
    testElement = document.createElement('div')
    document.body.appendChild(testElement)
  })

  afterEach(() => {
    document.body.removeChild(testElement)
    listener.clear();
    listener.restoreDefaultFilters()
  })

  function triggerKeyboardEvent(el, eventType, letterKey, options = {}) {

    const keyCode = letterKey.toUpperCase().charCodeAt(0);
    const eventObj = document.createEvent('Events') as any

    if (eventObj.initEvent) {
      eventObj.initEvent(eventType, true, true)
    }

    eventObj.keyCode = keyCode
    eventObj.which = keyCode

    // Handle additional options like ctrlKey, shiftKey, etc.
    for (const key in options) {
      if (options.hasOwnProperty(key)) {
        eventObj[key] = options[key]
      }
    }

    el.dispatchEvent ? el.dispatchEvent(eventObj) : el.fireEvent('on' + eventType, eventObj)
  }

  it('should initialize a singleton instance', () => {
    const anotherInstance = HotkeyListener.getInstance()
    expect(listener).toBe(anotherInstance)
  })

  it('should add and remove scopes', () => {
    listener.addScope('testScope')
    expect(listener.getScopes()).toContain('testScope')

    listener.removeScope('testScope')
    expect(listener.getScopes()).not.toContain('testScope')
  })

  it('should register and trigger on keydown for key combinations', (done) => {
      listener.addScope('testScope')

      listener.onKeydown({ keys: 'ctrl+b', scope: 'testScope' }, (event, handler) => {
          // NOTE: testing against capital 'B' because hotkey-js binds keys using capital letters
          expect(String.fromCharCode(event.keyCode)).toBe('B')
          expect(event.ctrlKey).toBe(true)
          done()
      });

      triggerKeyboardEvent(testElement, 'keydown', 'b', { ctrlKey: true })
  });

  it('should register and trigger on keyup for key combinations', (done) => {
      listener.addScope('testScope')

      listener.onKeyup({ keys: 'ctrl+a', scope: 'testScope' }, (event, handler) => {
          // NOTE: testing against capital 'A' because hotkey-js binds keys using capital letters
          expect(String.fromCharCode(event.keyCode)).toBe('A')
          expect(event.ctrlKey).toBe(true)
          done()
      });

      triggerKeyboardEvent(testElement, 'keyup', 'a', { ctrlKey: true })
  });

  it('should register and trigger on special keydown', (done) => {
    listener.addScope('testScope')

    listener.onSpecialKeydown({ keys: 'shift', scope: 'testScope' }, (event, handler) => {
      expect(event.shiftKey).toBe(true)
      done()
    });

    triggerKeyboardEvent(testElement, 'keydown', 'shift', {shiftKey: true})
  });

  it('should register and trigger on special keyup', (done) => {
    listener.addScope('testScope')

    listener.onSpecialKeyup({ keys: 'shift', scope: 'testScope' }, (event, handler) => {
      expect(event.shiftKey).toBe(true)
      done()
    });

    triggerKeyboardEvent(testElement, 'keyup', 'shift', {shiftKey: true})
  });

})
