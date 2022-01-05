<template>
<div>
    <div style="display: flex; flex-direction: row;">
        <v-btn @click="() => instances.undo()">Undo</v-btn>
        <v-btn @click="() => instances.redo()">Redo</v-btn>
    </div>
    <text_toolbar 
        :label_list="label_list" 
        :project_string_id="project_string_id"
        :label_file_colour_map="label_file_colour_map"
        :loading="loading"
        :request_refresh_from_project="true"
        :show_visibility_toggle="true"
        @change_label="change_label"
    />
    <div style="display: flex; flex-direction: row;">
        <text_sidebar
            :annotations="labels_to_render"
            :relations="relations_to_render"
            @on_annotation_hover="on_annotation_hover"
            @on_stop_hover="on_stop_hover"
            @on_relation_hover="on_relation_hover"
            @on_relation_stop_hover="on_relation_stop_hover"
        />
        <div style="width: 100%">
            <div 
                v-for="(sentense, sentense_index) in text_tokenized"
                :key="`${sentense}_${sentense_index}`"
                :style="`display: flex; flex-direction: row; border-bottom: 1px solid rgba(29, 209, 161, 0.5); background-color: ${sentense_is_odd(sentense_index) ? 'rgba(29, 209, 161, 0.1)' : 'white'}`"
            >
                <div style="display: flex; align-items: center; justify-content: center">{{ sentense_index + 1 }}.</div>
                <svg 
                    width="90%" 
                    style="height: 120px; margin-left: 10px;"
                    ref="svg_main_container"
                    @mousedown="(e) => on_selection_start(e, sentense_index)" 
                    @mouseup="(e) => on_selection_end(e, sentense_index)" 
                >   
                    <g v-if="path_is_been_drawn(sentense_index)">
                        <circle 
                            :cx="path.M1" 
                            :cy="path.M2" 
                            r="3" 
                            fill="black"
                        />
                        <path
                            stroke="black" 
                            fill="transparent"
                            :d="draw_arc" 
                        />
                        <path 
                            :d="`M ${path.Q3} ${path.M2} l -5, -5 l 10, 0 l -5, 5`" 
                            fill="black" 
                        />
                    </g>
                    <text_relation 
                        v-for="relation in relations_to_render.filter(rel => rel.sentense_index === sentense_index)"
                        :key="`relation_${relation.id}`"
                        :relation="relation"
                        :relation_hover="relation_hover"
                        @on_relation_hover="on_relation_hover"
                        @on_relation_stop_hover="on_relation_stop_hover"
                    />
                    <g 
                        :id="`text-to-annotate_${sentense_index}`" 
                        :ref="`text_to_annotate_${sentense_index}`" 
                        transform="translate(0, 65)"
                    >
                        <text 
                            v-for="token in sentense"
                            class="words"
                            :key="`text_token_${token.index}_sentense_index_${token.sentense_index}`"
                            :id="`text_token_${token.index}_sentense_index_${token.sentense_index}`" 
                            :ref="`text_token_${token.index}_sentense_index_${token.sentense_index}`" 
                            :x="token.token_start_coordinate" 
                            :y="token.token_start_height"
                        >
                            {{ token.word }}
                        </text>
                    </g>
                    <text_label
                        v-for="annotation in labels_to_render.filter(label => label.sentense_index === sentense_index)"
                        :key="`annotation_id_${annotation.id}`"
                        :annotation="annotation"
                        :hover_id="hover_id"
                        :relation_hover="relation_hover"
                        :sentence_index="sentense_index"
                        @on_annotation_hover="on_annotation_hover"
                        @on_stop_hover="on_stop_hover"
                        @on_add_relation="on_add_relation"
                    />
                </svg>
            </div>
        </div>
    </div>
</div>
</template>

<script>
import Vue from "vue";
import text_toolbar from "./text_toolbar.vue"
import text_label from "./text_label.vue"
import text_relation from "./text_relation.vue"
import text_sidebar from "./text_sidebar.vue"
import { TextInterface } from "./Command/TextCommand"

export default Vue.extend({
    name: "text_annotation_core",
    components: {
        text_toolbar,
        text_label,
        text_relation,
        text_sidebar
    },
    props: {
        project_string_id: {
            type: String,
            required: true
        },
        file: {},
        label_list: {
            type: Array,
            required: true
        },
        text: {
            type: String,
            default: "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus nascetur ridiculus mus cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus."
        }
    },
    data() {
        return {
            text_stringified: [],
            text_tokenized: [],
            set_x: null,
            set_y: null,
            selecction_width: 0,
            current_label: null,
            instances: new TextInterface(),
            element_width_dev: 300,
            hover_id: null,
            relation_hover: {
                relation_hover_id: null,
                start_label_id: null,
                end_label_id: null
            },
            drawing_relation: false,
            path: {
                M1: null,
                M2: null,
                Q1: null,
                Q2: null,
                Q3: null,
                Q4: null,
                sentense_index: null,
                start_annotation_id: null,
                end_annotation_id: null
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
        this.current_label = this.label_list[0]
    },
    computed: {
        path_is_been_drawn: function() {
            const { M1, M2, Q1, Q2, Q3, Q4, sentense_index } = this.path
            return sentense_index_cuuernt => M1 && M2 && Q1 && Q2 && Q3 && Q4 && sentense_index === sentense_index_cuuernt
        },
        draw_arc: function() {
            const { M1, M2, Q1, Q2, Q3, Q4 } = this.path
            return `M ${M1} ${M2} Q ${Q1} ${Q2} ${Q3} ${Q4 - 5}`
        },
        labels_to_render: function() {
            return this.instances.get("label")
        },
        relations_to_render: function() {
            return this.instances.get("relation")
        }
    },
    methods: {
        sentense_is_odd: function (sentense_index) {
            return sentense_index % 2
        }, 
        change_label: function(label) {
            this.current_label = label
        },
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
            const max_width = this.$refs.svg_main_container[0].width.baseVal.value
            const measure_words = this.text_tokenized.map(sentence => {
                let length_counter = 10;
                let height_counter = 0;
                const updated_sentense = sentence.map(token => {
                    const element = this.$refs[`text_token_${token.index}_sentense_index_${token.sentense_index}`][0]
                    const width_of_token = element.clientWidth
                    const updated_token = {...token, token_start_coordinate: length_counter, token_start_height: height_counter}
                    length_counter += (width_of_token + 5)
                    if (length_counter > max_width) {
                        length_counter = 10
                        height_counter += 20
                    }
                    return updated_token
                })

                return updated_sentense
            })

            this.text_tokenized = measure_words
        },
        on_svg_click: function(event, sentense_index) {
            const coordX_global = event.clientX;
            const coordY_global = event.clientY;
            const used_svg_wrapper_component = this.$refs.svg_main_container[sentense_index];
            var text_element = this.$refs[`text_to_annotate_${sentense_index}`][0]
            var topPos = text_element.getBoundingClientRect().top + window.scrollY;
            var leftPos = used_svg_wrapper_component.getBoundingClientRect().left + window.scrollX;

            const coordX_local = coordX_global - leftPos
            const coordY_local = coordY_global - topPos + 42

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

            const sel = window.getSelection();
            const range = sel.getRangeAt(0)
            const right = range.getBoundingClientRect().right - 300;

            const token_end = this.text_tokenized[sentense_index].reduce((prevValue, currentValue) => {
                const element_width = this.$refs[`text_token_${currentValue.index}_sentense_index_${sentense_index}`][0].clientWidth;
                const delta = element_width - (this.set_x + this.selecction_width)
                if (delta < 0) return prevValue
                return Math.min(prevValue, delta)
            }, 10000000000000000)
            this.selecction_width = this.selecction_width + token_end
        },
        on_selection_start: function(event, sentense_index) {
            if (!event.toElement.id) return
            const token_x = event.toElement.x.baseVal[0].value
            const token_y = 50 + event.toElement.y.baseVal[0].value
            console.log(token_y)
            const token_width = event.toElement.clientWidth
            console.log(token_x, token_width)
            console.log("ON KEY DOWN")
            this.set_x = token_x
            this.set_y = token_y
            this.selecction_width = token_width - token_x
            // this.on_svg_click(event, sentense_index)
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

            const sel = window.getSelection();
            const range = sel.getRangeAt(0)
            const width = range.getBoundingClientRect().width;

            if (selection_exists) {
                // this.selecction_width = width
                // if (this.set_x - coordX_global + 300 > 0) {
                //     this.set_x = this.set_x - width
                // }
                // this.spread_selection(sentense_index)
                this.instances.addLabelInstance(this.set_x, this.set_y, this.selecction_width, sentense_index, {...this.current_label})
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
            const relation_object = this.instances.get_relation_by_id(id)
            this.relation_hover = relation_object
        },
        on_relation_stop_hover: function() {
            this.relation_hover = {
                relation_hover_id: null,
                start_label_id: null,
                end_label_id: null
            }
        },
        on_mouse_move_listen: function(event) {
            const coordX_global = event.clientX;
            const element = this.$refs.svg_main_container[0];
            const leftPos = element.getBoundingClientRect().left + window.scrollX;

            const coordX_local = coordX_global - leftPos

            this.path.Q3 = coordX_local
            this.path.Q1 = coordX_local  / 2
        },
        on_add_relation: function(event, sentense_index, annotation_id) {
            if (this.drawing_relation) {
                const start_annotation = this.instances.get_label_by_id(this.path.start_annotation_id)
                const M1 = start_annotation.x + start_annotation.width / 2
                const end_annotation = this.instances.get_label_by_id(annotation_id)
                const H = end_annotation.x + end_annotation.width / 2
                if (start_annotation.id !== end_annotation.id && !this.relations_to_render.find(rel => rel.start_label === start_annotation.id && rel.end_label === end_annotation.id)) {
                    this.instances.addRelationInstance(M1, this.path.M2, H, start_annotation.id, end_annotation.id, sentense_index, {...this.current_label})
                }
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
            var used_svg_wrapper_component = this.$refs.svg_main_container[sentense_index];
            var text_element = this.$refs[`text_to_annotate_${sentense_index}`][0];
            var topPos = text_element.getBoundingClientRect().top + window.scrollY;
            var leftPos = used_svg_wrapper_component.getBoundingClientRect().left + window.scrollX;

            const coordX_local = coordX_global - leftPos
            const coordY_local = text_element.getBoundingClientRect().bottom - topPos - 10 + 37

            this.path.sentense_index = sentense_index
            this.path.M1 = coordX_local
            this.path.M2 = coordY_local
            this.path.Q2 = coordY_local - 30
            this.path.Q4 = coordY_local
            this.path.start_annotation_id = annotation_id

            window.addEventListener('mousemove', this.on_mouse_move_listen, true);
        }
    }
})
</script>


