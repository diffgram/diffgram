<template>
<div style="display: flex; flex-direction: row;">
    <div>
        <div>
            <h3 :style="`width: ${element_width_dev}px`">Labels: </h3>
            <ul>
                <li 
                    class="annotation-list"
                    @mouseover="on_annotation_hover(annotation.id)"
                    @mouseout="on_stop_hover"
                    v-for="annotation in annotations"
                >
                    Annotation #{{annotation.id}}
                </li>
            </ul>
        </div>
        <br />
        <div>
            <h3 :style="`width: ${element_width_dev}px`">Relations: </h3>
            <ul>
                <li 
                    class="annotation-list"
                    @mouseover="on_relation_hover(relation.id)"
                    @mouseout="on_relation_stop_hover"
                    v-for="relation in relations"
                >
                    Relation #{{relation.id}}
                </li>
            </ul>
        </div>
    </div>
    <div style="width: 100%">
        <div 
            v-for="(sentense, sentense_index) in text_tokenized" 
            style="display: flex; flex-direction: row; border-bottom: 1px solid black;"
        >
            <div>{{sentense_index + 1}}.</div>
            <svg 
                @mousedown="(e) => on_selection_start(e, sentense_index)" 
                @mouseup="(e) => on_selection_end(e, sentense_index)" 
                width="90%" 
                style="height: 120px; margin-left: 10px;" 
                id="trial"
            >
                <path
                    v-if="path.M1 && path.M2 && path.Q1 && path.Q2 && path.Q3 && path.Q4 && path.sentense_index === sentense_index" 
                    :d="`M ${path.M1} ${path.M2} Q ${path.Q1} ${path.Q2} ${path.Q3} ${path.Q4}`" 
                    stroke="black" 
                    fill="transparent"
                />
                <path
                    v-for="relation in relations.filter(rel => rel.sentense_index === sentense_index)"
                    :d="`M ${relation.M1} ${relation.M2} v -10 H ${relation.Q3} v 10`" 
                    :stroke="relation_hover_id === relation.id ? 'red' : 'black'" 
                    fill="transparent"
                />
                <g :id="`text-to-annotate_${sentense_index}`" transform="translate(0, 60)">
                    <text 
                        class="words" 
                        :id="`text_token_${token.index}_sentense_index_${token.sentense_index}`" 
                        :x="token.token_start_coordinate" 
                        v-for="token in sentense"
                    >
                        {{ token.word }}
                    </text>
                </g>
                <rect 
                    v-for="annotation in annotations.filter(ann => ann.sentense_index === sentense_index)"
                    :x="annotation.set_x" 
                    :y="annotation.set_y" 
                    :width="annotation.selecction_width"
                    height="20" 
                    :fill="hover_id && hover_id === annotation.id ? 'red' : '#2a58ff'"
                    opacity="0.4"
                    @mousedown.prevent="(e) => on_add_relation(e, sentense_index)"
                    style="cursor: pointer"
                />
            </svg>
        </div>
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
            annotations: [],
            relations: [],
            element_width_dev: 300,
            hover_id: null,
            relation_hover_id: null,
            drawing_relation: false,
            path: {
                M1: null,
                M2: null,
                Q1: null,
                Q2: null,
                Q3: null,
                Q4: null,
                sentense_index: null
            }
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
            var text_element = document.getElementById(`text-to-annotate_${sentense_index}`);
            var topPos = text_element.getBoundingClientRect().top + window.scrollY;
            var leftPos = element.getBoundingClientRect().left + window.scrollX;

            const coordX_local = coordX_global - leftPos
            const coordY_local = text_element.getBoundingClientRect().bottom - topPos - 10 + 37

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
                const delta = element_width  - (this.set_x + this.selecction_width) + this.element_width_dev
                if (delta < 0) return prevValue
                return Math.min(prevValue, delta)
            }, 10000000000000000)
            this.selecction_width = this.selecction_width + token_end - this.element_width_dev
        },
        on_selection_start: function(event, sentense_index) {
            if (!event.toElement.id) return
            console.log("ON KEY DOWN")
            this.selecction_width = 0
            this.on_svg_click(event, sentense_index)
        },
        on_selection_end: function(event, sentense_index) {
            if (!event.toElement.id) return
            if (this.drawing_relation) {
                this.drawing_relation = false
                this.path = {
                    M1: null,
                    M2: null,
                    Q1: null,
                    Q2: null,
                    Q3: null,
                    Q4: null,
                    sentense_index: null
                }
                return
            }
            console.log("ON KEY UP")
            const coordX_global = event.clientX;
            const selection_exists = Math.abs(this.set_x - coordX_global) > 10

            if (selection_exists) {
                this.selecction_width = Math.abs(this.set_x - coordX_global)
                this.spread_selection(sentense_index)
                this.annotations = [...this.annotations, { id: this.annotations.length + 1, set_x: this.set_x, set_y: this.set_y, selecction_width: this.selecction_width, sentense_index} ]
                document.getSelection().removeAllRanges()
            }
        },
        on_annotation_hover: function(id) {
            this.hover_id = id
        },
        on_stop_hover: function() {
            this.hover_id = null
        },
        on_relation_hover: function(id) {
            this.relation_hover_id = id
        },
        on_relation_stop_hover: function() {
            this.relation_hover_id = null
        },
        on_mouse_move_listen: function(event) {
            console.log("arroy moving")
            const coordX_global = event.clientX;
            var element = document.getElementById('trial');
            var leftPos = element.getBoundingClientRect().left + window.scrollX;

            const coordX_local = coordX_global - leftPos

            this.path.Q3 = coordX_local
            this.path.Q1 = coordX_local  / 2
        },
        on_add_relation: function(event, sentense_index) {
            if (this.drawing_relation) {
                this.relations = [...this.relations, {...this.path, id: this.relations.length + 1}]
                this.path = {
                    M1: null,
                    M2: null,
                    Q1: null,
                    Q2: null,
                    Q3: null,
                    Q4: null,
                    sentense_index: null
                }
                window.removeEventListener("mousemove", this.on_mouse_move_listen, true)
                this.drawing_relation = false
                return
            }
            console.log('Draw relation arrow')
            this.drawing_relation = true
            const coordX_global = event.clientX;
            var element = document.getElementById('trial');
            var text_element = document.getElementById(`text-to-annotate_${sentense_index}`);
            var topPos = text_element.getBoundingClientRect().top + window.scrollY;
            var leftPos = element.getBoundingClientRect().left + window.scrollX;

            const coordX_local = coordX_global - leftPos
            const coordY_local = text_element.getBoundingClientRect().bottom - topPos - 10 + 37

            this.path.sentense_index = sentense_index
            this.path.M1 = coordX_local
            this.path.M2 = coordY_local
            this.path.Q2 = coordY_local - 30
            this.path.Q4 = coordY_local

            window.addEventListener('mousemove', this.on_mouse_move_listen, true);
        }
    }
})
</script>

<style scoped>
.annotation-list:hover {
    text-decoration: underline;
    cursor: pointer;
}
</style>
