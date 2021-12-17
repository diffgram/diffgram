<template>
<div>
    <svg data-v-3863495a="" data-v-4e93770c="" version="1.1" xmlns="http://www.w3.org/2000/svg" direction="ltr" id="svg0:60" width="100%" style="height: 125.5px">
        <g data-v-3863495a="" transform="translate(0, 23.5)">
            <g data-v-3863495a="" style="cursor: pointer;">
                <path d="M 168.125 30
                v -20
                A 12 12 0 0 1 180.125 -2
                H 588
                " stroke="#74b8dc" stroke-width="1" fill-opacity="0">
                </path>
                <g>
                    <rect x="341.73828125" y="-12" width="72.6484375" height="20" fill="white"></rect>
                    <text x="378.0625" y="5" fill="currentColor" text-anchor="middle">isLorem</text>
                    </g></g>
                    <g data-v-3863495a="" transform="translate(0, 50)">
                        <text fill="currentColor" id="0:60" x="0" style="white-space: pre;">{{ text }}</text>
                        <g data-v-3863495a=""><line x1="127.4609375" y1="5" x2="208.7890625" y2="5" stroke="#e6d176" stroke-width="5" stroke-linecap="round">
                            </line><g style="cursor: pointer;"><circle r="3" fill="#e6d176" cx="127.9609375" cy="20"></circle>
                            <text x="124.9609375" y="20" fill="currentColor" dx="8" dy="0.35em">ORG</text>
                        </g>
                    </g>
                </g>
        </g>
    </svg>
    <br />
    <br />
    <br />
    <div>
        <svg @mousedown="on_selection_start" @mouseup="on_selection_end" width="90%" style="height: 125.5px; margin-left: 10px" id="trial">
            <g id="text-to-annotate" transform="translate(0, 23.5)">
                <text @dblclick.prevent="select_one_word" class="words" :id="`text_token_${token.index}`" :x="token.token_start_coordinate" v-for="token in text_tokenized">{{ token.word }}</text>
            </g>
            <rect 
                v-for="annotation in annotations" 
                :x="annotation.set_x" 
                :y="annotation.set_y" 
                :width="annotation.selecction_width" 
                height="20" 
                fill="#2a58ff"
                opacity="0.4"
            />
        </svg>
    </div>
</div>
</template>

<script>
import Vue from "vue";

export default Vue.extend({
    name: "text_annotation_core",
    props: {
        file: {},
        text: {
            type: String,
            default: "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
        }
    },
    data() {
        return {
            text_tokenized: [],
            set_x: null,
            set_y: null,
            selecction_width: 0,
            annotations: []
        }
    },
    mounted() {
        this.tokenize_text(this.text)
        setTimeout(() => {
            this.text_render_width()
        }, 2000)
    },
    methods: {
        tokenize_text: function(text) {
            const string_to_array = text.split(' ')
            const tokenized_text = string_to_array.map((word, index) => ({ word, index, token_start_coordinate: 0}))
            this.text_tokenized = tokenized_text
        },
        text_render_width: function() {
            let length_counter = 10;
            const measure_words = this.text_tokenized.map(token => {
                var element = document.getElementById(`text_token_${token.index}`);
                const width_of_token = element.clientWidth
                const updated_token = {...token, token_start_coordinate: length_counter}
                length_counter += (width_of_token + 5)
                return updated_token
            })

            this.text_tokenized = measure_words
        },
        on_svg_click: function(event) {
            const coordX_global = event.clientX;
            var element = document.getElementById('trial');
            var text_element = document.getElementById('text-to-annotate');
            var topPos = text_element.getBoundingClientRect().top + window.scrollY;
            var leftPos = element.getBoundingClientRect().left + window.scrollX;

            const coordX_local = coordX_global - leftPos
            const coordY_local = text_element.getBoundingClientRect().bottom - topPos - 10

            this.set_x = coordX_local
            this.set_y = coordY_local
        },
        spread_selection: function() {
            console.log("SPEREADING SELECT")
            const token_start = this.text_tokenized.reduce((prevValue, currentValue) => {
                const delta = this.set_x - currentValue.token_start_coordinate
                if (delta < 0) return prevValue
                return Math.min(prevValue, delta)
            }, 10000000000000000)
            this.set_x = this.set_x - token_start

            const token_end = this.text_tokenized.reduce((prevValue, currentValue) => {
                var element_width = document.getElementById(`text_token_${currentValue.index}`).clientWidth;
                const delta = element_width  - (this.set_x + this.selecction_width)
                if (delta < 0) return prevValue
                return Math.min(prevValue, delta)
            }, 10000000000000000)

            this.selecction_width = this.selecction_width + token_end
        },
        select_one_word: function() {
            console.log("ON DOUBLE CLICK")
            const s = window.getSelection();
            const oRange = s.getRangeAt(0);
            const oRect = oRange.getBoundingClientRect();
            var text_element = document.getElementById('text-to-annotate');
            var topPos = oRect.y - text_element.getBoundingClientRect().top + window.scrollY + 10;
            this.annotations = [...this.annotations, { set_x: oRect.x - 10, set_y: topPos, selecction_width: oRect.width} ]
        },
        on_selection_start: function(event) {
            console.log("ON KEY DOWN")
            this.selecction_width = 0
            this.on_svg_click(event)
        },
        on_selection_end: function(event) {
            console.log("ON KEY UP")
            const coordX_global = event.clientX;
            const selection_exists = Math.abs(this.set_x - coordX_global) > 10

            if (selection_exists) {
                this.selecction_width = Math.abs(this.set_x - coordX_global)
                this.spread_selection()
                this.annotations = [...this.annotations, { set_x: this.set_x, set_y: this.set_y, selecction_width: this.selecction_width} ]
            }
        }
    }
})
</script>
