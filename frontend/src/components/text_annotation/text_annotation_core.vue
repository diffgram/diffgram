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
                        <text data-v-5225550e="" data-v-3863495a="" fill="currentColor" id="0:60" x="0" style="white-space: pre;">{{ text }}</text>
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
        <svg @mousedown="on_selection_start" @mouseup="on_selection_end" width="100%" style="height: 125.5px" id="trial">
            <g transform="translate(0, 23.5)">
                <text id="text-to-annotate">{{text}}</text>
            </g>
            <rect 
                v-for="annotation in annotations" 
                :x="annotation.set_x" 
                :y="annotation.set_y" 
                :width="annotation.selecction_width" 
                height="3" 
                fill="green" 
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
        file: {}
    },
    data() {
        return {
            text: "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            set_x: null,
            set_y: null,
            selecction_width: 70,
            annotations: []
        }
    },
    methods: {
        on_svg_click: function(event) {
            const coordX_global = event.clientX;
            var element = document.getElementById('trial');
            var text_element = document.getElementById('text-to-annotate');
            var topPos = text_element.getBoundingClientRect().top + window.scrollY;
            var leftPos = element.getBoundingClientRect().left + window.scrollX;

            const coordX_local = coordX_global - leftPos
            const coordY_local = text_element.getBoundingClientRect().bottom - topPos + 10

            this.set_x = coordX_local
            this.set_y = coordY_local
        },
        on_selection_start: function(event) {
            this.selecction_width = 0
            this.on_svg_click(event)
        },
        on_selection_end: function(event) {
            const coordX_global = event.clientX;
            this.selecction_width = Math.abs(this.set_x - coordX_global)

            this.annotations = [...this.annotations, {set_x: this.set_x, set_y: this.set_y, selecction_width: this.selecction_width}]

            console.log(this.selecction_width)
        }
    }
})
</script>
