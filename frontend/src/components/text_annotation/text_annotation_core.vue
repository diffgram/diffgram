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
                v-if="relation_drawing"
            >
                <circle 
                    :cx="render_drawing_arrow.marker.x" 
                    :cy="render_drawing_arrow.marker.y" 
                    :fill="current_label.color"
                    r="3" 
                />
                <path
                    :stroke="current_label.color" 
                    :d="render_drawing_arrow.path" 
                    fill="transparent"
                />
                <path 
                    :d="`M ${render_drawing_arrow.arrow.x} ${render_drawing_arrow.arrow.y} l -5, -5 l 10, 0 l -5, 5`" 
                    :fill="current_label.color"
                />
            </g>
            <text 
                v-for="instance in instances"
                :key="`instance_${instance.id}`"
                :x="render_rects.find(rect => rect.instance_id === instance.id).x" 
                :y="render_rects.find(rect => rect.instance_id === instance.id).y - 3"
                :fill="hover_instance && (hover_instance.id === instance.id || hover_instance.start_instance === instance.id || hover_instance.end_instance === instance.id) ? 'red' : current_label.color"
                @mouseenter="() => on_instance_hover(instance.id)"
                @mousedown="() => on_start_draw_relation(instance.id)"
                @mouseleave="on_instance_stop_hover"
                style="font-size: 10px; cursor: pointer"
            >
                {{ current_label.text }}
            </text>
            <rect 
                v-for="rect in render_rects"
                :key="`rect_x_${rect.x}_y_${rect.y}_width_${rect.width}`"
                :fill="hover_instance && (hover_instance.id === rect.instance_id || hover_instance.start_instance === rect.instance_id || hover_instance.end_instance === rect.instance_id) ? 'red' : current_label.color"
                :x="rect.x"
                :y="rect.y"
                :width="rect.width"
                @mouseenter="() => on_instance_hover(rect.instance_id)"
                @mouseleave="on_instance_stop_hover"
                :height="rect.instance_type === 'annotation' ? 3 : 1"
                style="cursor: pointer"
            />
            <g 
                v-for="(line, index) in lines"
                :transform="`translate(0, ${25 + line.y})`"
                :key="`line_${index}`"
            >
                <text 
                    v-for="(token, index) in tokens.filter(token => token.line === index)"
                    @mousedown="() => on_start_draw_instance(token)"
                    @mouseup="() => on_finish_draw_instance(token)"
                    :key="`token_${index}`"
                    :x="token.start_x"
                    :fill="hover_instance && 
                        (
                            (hover_instance.start_token <= token.id && token.id <= hover_instance.end_token) || 
                            (hover_instance.start_token >= token.id && token.id >= hover_instance.end_token)
                        ) ? 'red' : 'black'"
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
                id: 0,
                text: "First",
                color: "blue"
            },
            rendering: true,
            relation_drawing: false,
            initial_words_measures: [],
            lines: [],
            tokens: [],
            instances: [],
            //effects
            hover_instance: null,
            //Helpers
            instance_in_progress: null,
            path: {},
            //Render constants
            additional_line_space: 20
        }
    },
    mounted() {
        this.initial_words_measures = this.text.split(' ')
        setTimeout(() => this.initialize_token_render(), 1000)
    },
    computed: {
        render_rects: function() {
            let rects_to_draw = [];
            this.instances.map(instance => {
                const instance_rects = this.draw_instance(instance)
                rects_to_draw = [...rects_to_draw, ...instance_rects]
            })
            this.find_intersections(rects_to_draw)
            rects_to_draw = [];
            this.instances.map(instance => {
                const instance_rects = this.draw_instance(instance)
                rects_to_draw = [...rects_to_draw, ...instance_rects]
            })
            this.find_intersections(rects_to_draw)
            return rects_to_draw
        },
        render_drawing_arrow: function() {
            const { x, y } = this.render_rects.find(rect => rect.instance_id === this.instance_in_progress.start_instance)
            return { 
                marker: {
                    x,
                    y
                },
                arrow: {
                    x: this.path.x,
                    y: this.path.y
                },
                path: `M ${x} ${y} Q ${this.path.x} ${this.path.y} ${this.path.x} ${this.path.y}`
             }
        }
    },
    methods: {
        initialize_token_render: function() {
            const fixed_svg_width = this.$refs.initial_svg_element.clientWidth;
            const tokens = [];
            let token_x_position = 40;

            this.initial_words_measures.map((word, index) => {
                const current_token_width = this.$refs[`word_${index}`][0].getBoundingClientRect().width

                if (this.lines.length === 0) {
                    this.lines.push({ id: 0, y: 5, initial_y: 5 })
                }
                if (token_x_position + current_token_width > fixed_svg_width) {
                    this.lines.push({id: this.lines.length, y: this.lines[this.lines.length - 1].y + 40, initial_y: this.lines[this.lines.length - 1].y + 40 })
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
        // function to draw relations between instances
        on_start_draw_relation: function(instance_id) {
            if (!this.relation_drawing) {
                this.relation_drawing = true
                this.instance_in_progress = {
                    id: this.instances.length,
                    type: "relation",
                    start_instance: instance_id,
                    label_id: this.current_label.id,
                    level: 0
                }
                window.addEventListener('mousemove', this.draw_relation_listener)
                return
            }

            this.relation_drawing = false;
            this.instance_in_progress.end_instance = instance_id;
            this.instances.push(this.instance_in_progress)
            this.instance_in_progress = null;
            this.path = {};
            window.removeEventListener('mousemove', this.draw_relation_listener)
        },
        draw_relation_listener: function(e) {
            this.path = {
                x: e.clientX,
                y: e.clientY
            }
        },
        //function to hover on instance
        on_instance_hover: function(instance_id) {
            const instance = {...this.instances.find(instance => instance.id === instance_id)}
            this.hover_instance = instance
        },
        on_instance_stop_hover: function() {
            this.hover_instance = null
        },
        // function to initialize drawing new instance
        on_start_draw_instance: function(start_token) {
            this.instance_in_progress = {
                id: this.instances.length,
                type: "annotation",
                start_token: start_token.id,
                label_id: this.current_label.id,
                level: 0
            }
        },
        // function to finish drawing instance and remove selection
        on_finish_draw_instance: function(end_token) {
            this.instance_in_progress.end_token = end_token.id
            const instance_exists = this.instances.find(instance => 
                instance.start_token === this.instance_in_progress.start_token && instance.end_token === this.instance_in_progress.end_token
                ||
                instance.end_token === this.instance_in_progress.start_token && instance.start_token === this.instance_in_progress.end_token
                )
            if (!instance_exists) {
                this.instances.push(this.instance_in_progress)
            }
            this.instance_in_progress = null
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
        // Find intersection and update level of the instance
        find_intersections: function(rects_to_draw) {
            rects_to_draw.map((rect, index) => {
                rects_to_draw.map((comp_rect, comp_index) => {
                    if (index === comp_index) return
                    if (rect.line !== comp_rect.line) return
                    if (rect.x <= comp_rect.x && rect.x + rect.width > comp_rect.x && rect.y === comp_rect.y) {
                        if (rect.width === comp_rect.width) {
                            if (comp_rect.instance_type === "relation") return comp_rect.y = comp_rect.y - this.additional_line_space
                            else {
                                return rect.y = rect.y - this.additional_line_space
                            }
                        }
                        if (rect.width > comp_rect.width) return rect.y = rect.y - this.additional_line_space
                        comp_rect.y = comp_rect.y - this.additional_line_space
                        this.find_intersections(rects_to_draw)
                    }
                })
            })
            rects_to_draw.map((rect, index) => {
                rects_to_draw.map((comp_rect, comp_index) => {
                    if (index === comp_index) return
                    if (rect.line !== comp_rect.line) return
                    if (rect.x <= comp_rect.x && rect.x + rect.width > comp_rect.x && rect.y === comp_rect.y) {
                        if (rect.width === comp_rect.width) {
                            if (comp_rect.instance_type === "relation") return comp_rect.y = comp_rect.y - this.additional_line_space
                            else {
                                return rect.y = rect.y - this.additional_line_space
                            }
                        }
                        if (rect.width > comp_rect.width) return rect.y = rect.y - this.additional_line_space
                        comp_rect.y = comp_rect.y - this.additional_line_space
                        this.find_intersections(rects_to_draw)
                    }
                })
            })

            const rects_lines_map = rects_to_draw.reduce(
                (entryMap, e) => entryMap.set(e.line, [...entryMap.get(e.line)||[], e]),
                new Map()
            )

            this.lines.forEach(line => line.y = line.initial_y)
            
            this.lines.map(line => {
                if (rects_lines_map.get(line.id)) {
                    const rect_levels = [...rects_lines_map.get(line.id).map(rect => rect.y)]
                    const move_strings_level = (Math.max(...rect_levels) - Math.min(...rect_levels)) / this.additional_line_space
                    this.update_line_height(line.id, move_strings_level)
                }
            })
        },
        // Update line height if there are few levels of instances
        update_line_height: function(line_id, level) {
            this.lines.map(line => {
                if (line.id >= line_id) {
                    line.y = line.y + level * this.additional_line_space
                }
            })
        },
        // draw_instance - is only returning rects that have to be drawn
        draw_instance: function(instance) {
            let starting_token;
            let end_token;
            if (instance.type === 'annotation') {
                starting_token = this.tokens.find(token => token.id === instance.start_token)
                end_token = this.tokens.find(token => token.id === instance.end_token)
            } else {
                const start_instance = this.instances.find(find_instance => find_instance.id === instance.start_instance)
                starting_token = this.tokens.find(token => token.id === start_instance.start_token)
                const end_instance = this.instances.find(find_instance => find_instance.id === instance.end_instance)
                end_token = this.tokens.find(token => token.id === end_instance.end_token)
            }
            if (starting_token.id === end_token.id) {
                const rect = {
                    instance_id: instance.id,
                    x: starting_token.start_x,
                    y: this.lines[starting_token.line].y + 3,
                    line: starting_token.line,
                    width: starting_token.width,
                    instance_type: instance.type
                }
                return [rect]
            }
            
            if (starting_token.line === end_token.line) {
                if (starting_token.id < end_token.id) {
                    const rect = {
                        instance_id: instance.id,
                        x: starting_token.start_x,
                        y: this.lines[starting_token.line].y + 3,
                        line: starting_token.line,
                        width: end_token.start_x + end_token.width - starting_token.start_x,
                        instance_type: instance.type
                    }
    
                    return [rect]
                } else {
                    const rect = {
                        instance_id: instance.id,
                        x: end_token.start_x,
                        y: this.lines[end_token.line].y + 3,
                        line: starting_token.line,
                        width: starting_token.start_x + starting_token.width - end_token.start_x,
                        instance_type: instance.type
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
                                instance_id: instance.id,
                                x: first_token_in_the_line.start_x,
                                y: this.lines[first_token_in_the_line.line].y + 3,
                                line: i,
                                width: starting_token.start_x + starting_token.width - first_token_in_the_line.start_x,
                                instance_type: instance.type
                            }
                            rects.push(rect)
                        }
                        else if (i === end_token.line) {
                            const last_token_in_the_line = this.tokens.filter(token => token.line == end_token.line)
                            const rect = {
                                instance_id: instance.id,
                                x: end_token.start_x,
                                y: this.lines[end_token.line].y + 3,
                                line: i,
                                width: last_token_in_the_line[last_token_in_the_line.length - 1].start_x + last_token_in_the_line[last_token_in_the_line.length - 1].width - end_token.start_x,
                                instance_type: instance.type
                            }
                            rects.push(rect)
                        }
                        else {
                            const last_token_in_the_line = this.tokens.filter(token => token.line == this.lines[i].id)
                            const first_token_in_the_line = this.tokens.find(token => token.line == this.lines[i].id)
                            const rect = {
                                instance_id: instance.id,
                                x: first_token_in_the_line.start_x,
                                y: this.lines[first_token_in_the_line.line].y + 3,
                                line: i,
                                width: last_token_in_the_line[last_token_in_the_line.length - 1].start_x + last_token_in_the_line[last_token_in_the_line.length - 1].width - first_token_in_the_line.start_x,
                                instance_type: instance.type
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
                                instance_id: instance.id,
                                x: starting_token.start_x,
                                y: this.lines[starting_token.line].y + 3,
                                line: i,
                                width: last_token_in_the_line[last_token_in_the_line.length - 1].start_x + last_token_in_the_line[last_token_in_the_line.length - 1].width - starting_token.start_x,
                                instance_type: instance.type
                            }
                            rects.push(rect)
                        }
                        else if (i === end_token.line) {
                            const first_token_in_the_line = this.tokens.find(token => token.line == end_token.line)
                            const rect = {
                                instance_id: instance.id,
                                x: first_token_in_the_line.start_x,
                                y: this.lines[first_token_in_the_line.line].y + 3,
                                line: i,
                                width: end_token.start_x + end_token.width - first_token_in_the_line.start_x,
                                instance_type: instance.type
                            }
                            rects.push(rect)
                        }
                        else {
                            const last_token_in_the_line = this.tokens.filter(token => token.line == this.lines[i].id)
                            const first_token_in_the_line = this.tokens.find(token => token.line == this.lines[i].id)
                            const rect = {
                                instance_id: instance.id,
                                x: first_token_in_the_line.start_x,
                                y: this.lines[first_token_in_the_line.line].y + 3,
                                line: i,
                                width: last_token_in_the_line[last_token_in_the_line.length - 1].start_x + last_token_in_the_line[last_token_in_the_line.length - 1].width - first_token_in_the_line.start_x,
                                instance_type: instance.type
                            }
                            rects.push(rect)
                        }
                    }
                    return rects
                }
            }
            const trial_rect = {
                x: starting_token.start_x,
                y: this.lines[starting_token.line].y + 3,
                width: starting_token.width,
                instance_type: instance.type
            }
            return [trial_rect]
        }
    }
})
</script>
