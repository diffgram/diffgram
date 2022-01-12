<template>
    <svg 
        ref="initial_svg_element" 
        version="1.1" 
        xmlns="http://www.w3.org/2000/svg" 
        direction="ltr" 
        id="svg0:60" 
        width="95%" 
        style="height: 1000.5px">
        <g v-if="rendering" transform="translate(0, 23.5)">
            <text 
                v-for="(word, index) in initial_words_measures"
                :key="word"
                :ref="`word_${index}`"
                x="40" 
                y="5" 
                fill="white" 
                text-anchor="middle">
                    {{ word }}
            </text>
        </g>
        <g v-else>
            <g 
                v-for="label in labels"
                :key="`label_${label.id}`"
                @mouseenter="() => on_label_hover(label)"
                @mouseleave="on_label_stop_hover"
            >
                <text>{{ label.text }}</text>
                <rect 
                    v-for="rect in draw_label(label)"
                    :key="`rect_x_${rect.x}_y_${rect.y}_width_${rect.width}`"
                    :x="rect.x"
                    :y="rect.y"
                    :width="rect.width"
                    :fill="hover_label && hover_label.id === label.id ? 'red' : label.color"
                    opacity="0.4"
                    height="2"
                />
            </g>
            <g 
                v-for="(line, index) in lines"
                :transform="`translate(0, ${25 + line.y})`"
                :key="`line_${index}`"
            >
                <text 
                    v-for="(token, index) in tokens.filter(token => token.line === index)"
                    @mousedown="() => on_start_draw_label(token)"
                    @mouseup="() => on_finish_draw_label(token)"
                    :key="`token_${index}`"
                    :x="token.start_x"
                    :fill="hover_label && ((hover_label.start_token <= token.id && token.id <= hover_label.end_token) || (hover_label.start_token >= token.id && token.id >= hover_label.end_token)) ? 'red' : 'black'"
                >
                    {{ token.word }}
                </text>
            </g>
        </g>
    </svg>
</template>

<script>
import Vue from "vue";

export default Vue.extend({
    name: "text_annotation_core",
    props: {
        file: {},
        text: {
            type: String,
            default: `There are many variations of passages of Lorem Ipsum available, but the majority have suffered alteration in some form, by injected humour, or randomised words which don't look even slightly believable. If you are going to use a passage of Lorem Ipsum, you need to be sure there isn't anything embarrassing hidden in the middle of text. All the Lorem Ipsum generators on the Internet tend to repeat predefined chunks as necessary, making this the first true generator on the Internet. It uses a dictionary of over 200 Latin words, combined with a handful of model sentence structures, to generate Lorem Ipsum which looks reasonable. The generated Lorem Ipsum is therefore always free from repetition, injected humour, or non-characteristic words etc. There are many variations of passages of Lorem Ipsum available, but the majority have suffered alteration in some form, by injected humour, or randomised words which don't look even slightly believable. If you are going to use a passage of Lorem Ipsum, you need to be sure there isn't anything embarrassing hidden in the middle of text. All the Lorem Ipsum generators on the Internet tend to repeat predefined chunks as necessary, making this the first true generator on the Internet. It uses a dictionary of over 200 Latin words, combined with a handful of model sentence structures, to generate Lorem Ipsum which looks reasonable. The generated Lorem Ipsum is therefore always free from repetition, injected humour, or non-characteristic words etc.`
        }
    },
    data() {
        return {
            current_label: {
                text: "First",
                color: "blue"
            },
            rendering: true,
            initial_words_measures: [],
            lines: [],
            tokens: [],
            labels: [],
            //effects
            hover_label: null,
            //Helpers
            label_in_progress: null
        }
    },
    mounted() {
        this.initial_words_measures = this.text.split(' ')
        setTimeout(() => this.initialize_token_render(), 1000)
    },
    methods: {
        initialize_token_render: function() {
            const fixed_svg_width = this.$refs.initial_svg_element.clientWidth;
            const tokens = [];
            let token_x_position = 40;

            this.initial_words_measures.map((word, index) => {
                const current_token_width = this.$refs[`word_${index}`][0].getBoundingClientRect().width

                if (this.lines.length === 0) {
                    this.lines.push({ id: 0, y: 5 })
                }
                if (token_x_position + current_token_width > fixed_svg_width) {
                    this.lines.push({id: this.lines.length, y: this.lines[this.lines.length - 1].y + 40 })
                    token_x_position = 40
                }

                const token = {
                    word,
                    id: index,
                    width: current_token_width,
                    start_x: token_x_position,
                    line: this.lines.length - 1
                }
                tokens.push(token)
                token_x_position = token_x_position + current_token_width + 5
            })

            this.tokens = tokens
            this.rendering = false
        },
        //function to hover on label
        on_label_hover: function(label) {
            this.hover_label = label
        },
        on_label_stop_hover: function() {
            this.hover_label = null
        },
        // function to initialize drawing new label
        on_start_draw_label: function(start_token) {
            this.label_in_progress = {
                id: this.labels.length,
                start_token: start_token.id,
                color: this.current_label.color,
                text: this.current_label.text,
                level: 0
            }
        },
        // function to finish drawing label and remove selection
        on_finish_draw_label: function(end_token) {
            this.label_in_progress.end_token = end_token.id
            this.labels.push(this.label_in_progress)
            this.label_in_progress = null
            if (window.getSelection) {
                if (window.getSelection().empty) {  // Chrome
                    window.getSelection().empty();
                } else if (window.getSelection().removeAllRanges) {  // Firefox
                    window.getSelection().removeAllRanges();
                }
                } else if (document.selection) {  // IE?
                document.selection.empty();
            }
        },
        // draw_label - is only returning rects that have to be drawn
        draw_label: function(label) {
            const starting_token = this.tokens.find(token => token.id === label.start_token)
            const end_token = this.tokens.find(token => token.id === label.end_token)
            if (starting_token.id === end_token.id) {
                const rect = {
                    x: this.tokens[label.start_token].start_x,
                    y: this.lines[this.tokens[label.start_token].line].y + 3,
                    line: starting_token.line,
                    width: this.tokens[label.start_token].width
                }
                return [rect]
            }
            
            if (starting_token.line === end_token.line) {
                if (starting_token.id < end_token.id) {
                    const rect = {
                        x: this.tokens[label.start_token].start_x,
                        y: this.lines[this.tokens[label.start_token].line].y + 3,
                        line: starting_token.line,
                        width: this.tokens[label.end_token].start_x + this.tokens[label.end_token].width - this.tokens[label.start_token].start_x
                    }
    
                    return [rect]
                } else {
                    const rect = {
                        x: this.tokens[label.end_token].start_x,
                        y: this.lines[this.tokens[label.end_token].line].y + 3,
                        line: starting_token.line,
                        width: this.tokens[label.start_token].start_x + this.tokens[label.start_token].width - this.tokens[label.end_token].start_x
                    }
    
                    return [rect]
                }
            }

            if (starting_token.line !== end_token.line) {
                if (starting_token.id > end_token.id) {
                    const rects = [];
                    for (let i = end_token.line; i <= starting_token.line; ++i) {
                        if (i === starting_token.line) {
                            const first_token_in_the_line = this.tokens.find(token => token.line == starting_token.line)
                            const rect = {
                                x: first_token_in_the_line.start_x,
                                y: this.lines[first_token_in_the_line.line].y + 3,
                                line: i,
                                width: this.tokens[label.start_token].start_x + this.tokens[label.start_token].width - first_token_in_the_line.start_x
                            }
                            rects.push(rect)
                        }
                        else if (i === end_token.line) {
                            const last_token_in_the_line = this.tokens.filter(token => token.line == end_token.line)
                            const rect = {
                                x: this.tokens[label.end_token].start_x,
                                y: this.lines[this.tokens[label.end_token].line].y + 3,
                                line: i,
                                width: last_token_in_the_line[last_token_in_the_line.length - 1].start_x + last_token_in_the_line[last_token_in_the_line.length - 1].width - this.tokens[label.end_token].start_x
                            }
                            rects.push(rect)
                        }
                        else {
                            const last_token_in_the_line = this.tokens.filter(token => token.line == this.lines[i].id)
                            const first_token_in_the_line = this.tokens.find(token => token.line == this.lines[i].id)
                            const rect = {
                                x: first_token_in_the_line.start_x,
                                y: this.lines[first_token_in_the_line.line].y + 3,
                                line: i,
                                width: last_token_in_the_line[last_token_in_the_line.length - 1].start_x + last_token_in_the_line[last_token_in_the_line.length - 1].width - first_token_in_the_line.start_x
                            }
                            rects.push(rect)
                        }
                    }
                    return rects
                } else {
                    const rects = [];
                    for (let i = starting_token.line; i <= end_token.line; ++i) {
                        if (i === starting_token.line) {
                            const last_token_in_the_line = this.tokens.filter(token => token.line == starting_token.line)
                            const rect = {
                                x: this.tokens[label.start_token].start_x,
                                y: this.lines[this.tokens[label.start_token].line].y + 3,
                                line: i,
                                width: last_token_in_the_line[last_token_in_the_line.length - 1].start_x + last_token_in_the_line[last_token_in_the_line.length - 1].width - this.tokens[label.start_token].start_x
                            }
                            rects.push(rect)
                        }
                        else if (i === end_token.line) {
                            const first_token_in_the_line = this.tokens.find(token => token.line == end_token.line)
                            const rect = {
                                x: first_token_in_the_line.start_x,
                                y: this.lines[first_token_in_the_line.line].y + 3,
                                line: i,
                                width: this.tokens[label.end_token].start_x + this.tokens[label.end_token].width - first_token_in_the_line.start_x
                            }
                            rects.push(rect)
                        }
                        else {
                            const last_token_in_the_line = this.tokens.filter(token => token.line == this.lines[i].id)
                            const first_token_in_the_line = this.tokens.find(token => token.line == this.lines[i].id)
                            const rect = {
                                x: first_token_in_the_line.start_x,
                                y: this.lines[first_token_in_the_line.line].y + 3,
                                line: i,
                                width: last_token_in_the_line[last_token_in_the_line.length - 1].start_x + last_token_in_the_line[last_token_in_the_line.length - 1].width - first_token_in_the_line.start_x
                            }
                            rects.push(rect)
                        }
                    }
                    return rects
                }
            }
            const trial_rect = {
                x: this.tokens[label.start_token].start_x,
                y: this.lines[this.tokens[label.start_token].line].y + 3,
                width: this.tokens[label.start_token].width
            }
            return [trial_rect]
        }
    }
})
</script>
