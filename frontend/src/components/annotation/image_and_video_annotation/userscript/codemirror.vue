<template>
  <div id="codemirror">
    <textarea ref="textarea"
              :name="name"
              :placeholder="placeholder"
              data-cy="code_mirror"
              >
    </textarea>
  </div>
</template>

<script>

// Modified from: https://github.com/surmon-china/vue-codemirror

/*
 * Use example

............... in script:

  import codemirror from './codemirror.vue'
  components : {
        codemirror
      },

............... in data:

  cmOptions: {
    tabSize: 4,
    mode: 'javascript',
    lineNumbers: true,
    line: true,
    // more CodeMirror options...
  },

............... in html:
 
  <codemirror ref="testeditor"
                v-model="content"
                :options="cmOptions"
                >
  </codemirror>

/*
// https://codepen.io/CSWApps/pen/ybGbJK
// why multiple imports -> https://github.com/codemirror/CodeMirror/issues/5484
// why in mounted -> https://github.com/codemirror/CodeMirror/issues/4180
// careful need multiple imports and not as expected to get this to work

other lessons link https://docs.google.com/document/d/1g67n4FTLejW3VjwO-HirocWfj3vLaD1tS9vCUs91gtw/edit#heading=h.zbth2nr2giub

 */

// IMPORTANT. Otherwise styles will break. See https://github.com/codemirror/CodeMirror/issues/5484
import CodeMirror from 'codemirror/lib/codemirror.js';
import 'codemirror/mode/javascript/javascript.js';
import './codemirror.css'   // important!
import Vue from "vue";

  // export
  export default Vue.extend({
    name: 'codemirror',
    data() {
      return {
        content: '',
        codemirror: null,
        cminstance: null
      }
    },
    props: {
      code: String,
      value: String,
      marker: Function,
      unseenLines: Array,
      name: {
        type: String,
        default: 'codemirror'
      },
      placeholder: {
        type: String,
        default: ''
      },
      options: {
        type: Object,
        default: () => ({})
      },
      events: {
        type: Array,
        default: () => ([])
      },
      globalOptions: {
        type: Object,
        default: () => ({})
      },
      globalEvents: {
        type: Array,
        default: () => ([])
      },
      width: {
        type: Number,
        default: 750
      },
      height: {
        type: Number,
        default: 750
      }
    },
    watch: {
      options: {
        deep: true,
        handler(options) {
          for (const key in options) {
            this.cminstance.setOption(key, options[key])
          }
        }
      },

      width(newVal){
        this.codemirror.setSize(newVal, this.height)
      },

      height(newVal){
        this.codemirror.setSize(this.width, newVal)
      },

      code(newVal) {
        this.handerCodeChange(newVal)
      },
      value(newVal) {
        this.handerCodeChange(newVal)
      },
    },
    methods: {
      initialize() {
        const cmOptions = Object.assign({}, this.globalOptions, this.options)

        this.codemirror = CodeMirror.fromTextArea(this.$refs.textarea, cmOptions)
        this.cminstance = this.codemirror
        this.cminstance.setValue(this.code || this.value || this.content)
        this.codemirror.setSize(this.width, this.height)

        // This is the main "watch for changes and get value" thing

        this.cminstance.on('change', cm => {
          this.content = cm.getValue()
          if (this.$emit) {
            this.$emit('input', this.content)
          }
        })

        // (note during modifications - this feels a bit heavy but it
        // appears to work so leaving it for now.

        const tmpEvents = {}
        const allEvents = [
          'scroll',
          'changes',
          'beforeChange',
          'cursorActivity',
          'keyHandled',
          'inputRead',
          'electricInput',
          'beforeSelectionChange',
          'viewportChange',
          'swapDoc',
          'gutterClick',
          'gutterContextMenu',
          'focus',
          'blur',
          'refresh',
          'optionChange',
          'scrollCursorIntoView',
          'update'
        ]
        .concat(this.events)
        .concat(this.globalEvents)
        .filter(e => (!tmpEvents[e] && (tmpEvents[e] = true)))
        .forEach(event => {

          this.cminstance.on(event, (...args) => {
         
            this.$emit(event, ...args)
            const lowerCaseEvent = event.replace(/([A-Z])/g, '-$1').toLowerCase()
            if (lowerCaseEvent !== event) {
              this.$emit(lowerCaseEvent, ...args)
            }
          })
        })

        this.$emit('ready', this.codemirror)

        // (note during modifications - not sure what this was for)
        //this.unseenLineMarkers()

        // prevents funky dynamic rendering
        this.refresh()
      },
      refresh() {
        this.$nextTick(() => {
          this.cminstance.refresh()
        })
      },
      destroy() {
        // garbage cleanup
        const element = this.cminstance.doc.cm.getWrapperElement()
        element && element.remove && element.remove()
      },
      handerCodeChange(newVal) {
        const cm_value = this.cminstance.getValue()
        if (newVal !== cm_value) {
          const scrollInfo = this.cminstance.getScrollInfo()
          this.cminstance.setValue(newVal)
          this.content = newVal
          this.cminstance.scrollTo(scrollInfo.left, scrollInfo.top)
        }
        this.unseenLineMarkers()
      },
      unseenLineMarkers() {
        if (this.unseenLines !== undefined && this.marker !== undefined) {
          this.unseenLines.forEach(line => {
            const info = this.cminstance.lineInfo(line)
            this.cminstance.setGutterMarker(line, 'breakpoints', info.gutterMarkers ? null : this.marker())
          })
        }
      }
    },
    mounted() {
      this.initialize()
    },
    beforeDestroy() {
      this.destroy()
    }
  })
</script>
