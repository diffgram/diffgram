<template>
<div>
    <div v-for="(sentense, sentense_index) in text_tokenized" style="border-bottom: 1px solid black;">
        <svg 
            @mousedown="(e) => on_selection_start(e, sentense_index)" 
            @mouseup="(e) => on_selection_end(e, sentense_index)" width="90%" 
            style="height: 125.5px; margin-left: 10px;" 
            id="trial"
        >
            <g :id="`text-to-annotate_${sentense_index}`" transform="translate(0, 23.5)">
                <text 
                    @dblclick.prevent="select_one_word(token.sentense_index)" 
                    class="words" 
                    :id="`text_token_${token.index}_sentense_index_${token.sentense_index}`" 
                    :x="token.token_start_coordinate" 
                    v-for="token in sentense">{{ token.word }}</text>
            </g>
            <rect 
                v-for="annotation in annotations.filter(ann => ann.sentense_index === sentense_index)"
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
            default: "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus."
        }
    },
    data() {
        return {
            text_stringified: [],
            text_tokenized: [],
            set_x: null,
            set_y: null,
            selecction_width: 0,
            annotations: []
        }
    },
    mounted() {
        this.stringify_test(this.text)
        this.text_stringified.map((sentence, sentense_index) => {
            this.tokenize_text(sentence, sentense_index)
        })
        setTimeout(() => {
            this.text_render_width()
        }, 2000)
    },
    methods: {
        stringify_test: function(text) {
            const stringified = text.split('. ')
            this.text_stringified = stringified
        },
        tokenize_text: function(text, sentense_index) {
            const string_to_array = text.split(' ')
            const tokenized_text = string_to_array.map((word, index) => ({ word, index, sentense_index, token_start_coordinate: 0}))
            this.text_tokenized.push(tokenized_text)
        },
        text_render_width: function() {
            const measure_words = this.text_tokenized.map(sentence => {
                let length_counter = 10;
                const updated_sentense = sentence.map(token => {
                    var element = document.getElementById(`text_token_${token.index}_sentense_index_${token.sentense_index}`);
                    const width_of_token = element.clientWidth
                    const updated_token = {...token, token_start_coordinate: length_counter}
                    length_counter += (width_of_token + 5)
                    return updated_token
                })

                return updated_sentense
            })

            this.text_tokenized = measure_words
        },
        on_svg_click: function(event, sentense_index) {
            const coordX_global = event.clientX;
            var element = document.getElementById('trial');
            console.log(sentense_index)
            var text_element = document.getElementById(`text-to-annotate_${sentense_index}`);
            var topPos = text_element.getBoundingClientRect().top + window.scrollY;
            var leftPos = element.getBoundingClientRect().left + window.scrollX;

            const coordX_local = coordX_global - leftPos
            const coordY_local = text_element.getBoundingClientRect().bottom - topPos - 10

            this.set_x = coordX_local
            this.set_y = coordY_local
        },
        spread_selection: function(sentense_index) {
            console.log("SPEREADING SELECT")
            const token_start = this.text_tokenized[sentense_index].reduce((prevValue, currentValue) => {
                const delta = this.set_x - currentValue.token_start_coordinate
                if (delta < 0) return prevValue
                return Math.min(prevValue, delta)
            }, 10000000000000000)
            this.set_x = this.set_x - token_start

            const token_end = this.text_tokenized[sentense_index].reduce((prevValue, currentValue) => {
                var element_width = document.getElementById(`text_token_${currentValue.index}_sentense_index_${sentense_index}`).clientWidth;
                const delta = element_width  - (this.set_x + this.selecction_width)
                if (delta < 0) return prevValue
                return Math.min(prevValue, delta)
            }, 10000000000000000)
            this.selecction_width = this.selecction_width + token_end
        },
        select_one_word: function(sentense_index) {
            console.log("ON DOUBLE CLICK")
            const s = window.getSelection();
            const oRange = s.getRangeAt(0);
            const oRect = oRange.getBoundingClientRect();
            var text_element = document.getElementById(`text-to-annotate_${sentense_index}`);
            var topPos = oRect.y - text_element.getBoundingClientRect().top + window.scrollY + 10;
            this.annotations = [...this.annotations, { set_x: oRect.x - 10, set_y: topPos, selecction_width: oRect.width, sentense_index} ]
            document.getSelection().removeAllRanges()
        },
        on_selection_start: function(event, sentense_index) {
            console.log("ON KEY DOWN")
            this.selecction_width = 0
            this.on_svg_click(event, sentense_index)
        },
        on_selection_end: function(event, sentense_index) {
            console.log("ON KEY UP")
            const coordX_global = event.clientX;
            const selection_exists = Math.abs(this.set_x - coordX_global) > 10

            if (selection_exists) {
                this.selecction_width = Math.abs(this.set_x - coordX_global)
                this.spread_selection(sentense_index)
                this.annotations = [...this.annotations, { set_x: this.set_x, set_y: this.set_y, selecction_width: this.selecction_width, sentense_index} ]
                document.getSelection().removeAllRanges()
            }
        }
    }
})
</script>
