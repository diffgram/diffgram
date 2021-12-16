<template>
    <svg data-v-3863495a="" data-v-4e93770c="" version="1.1" xmlns="http://www.w3.org/2000/svg" direction="ltr" id="svg0:60" width="100%" style="height: 125.5px">
    <defs data-v-3863495a="">
        <marker data-v-3863495a="" id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path data-v-3863495a="" d="M 0 0 L 10 5 L 0 10 z" stroke="#74b8dc" fill="#74b8dc"></path>
        </marker>
        </defs>
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
                        <text data-v-5225550e="" data-v-3863495a="" fill="currentColor" id="0:60" x="0" style="white-space: pre;">After bowling Somerset out for 83 on the opening morning at </text>
                        <g data-v-3863495a=""><line x1="127.4609375" y1="5" x2="208.7890625" y2="5" stroke="#e6d176" stroke-width="5" stroke-linecap="round">
                            </line><g style="cursor: pointer;"><circle r="3" fill="#e6d176" cx="127.9609375" cy="20"></circle>
                            <text x="124.9609375" y="20" fill="currentColor" dx="8" dy="0.35em">ORG</text>
                        </g>
                    </g>
                </g>
        </g>
    </svg>
</template>

<script>
import Vue from "vue";
import axios from "axios"

export default Vue.extend({
    name: "text_annotation_core",
    props: {
        file: {}
    },
    async mounted() {
        console.log("Fetch from: ", this.file.text.url_signed)
        const get_file = await axios.get("https://diffgram-storage-v.s3.amazonaws.com/projects/text/1/1")
        console.log(get_file)
    }
})
</script>
