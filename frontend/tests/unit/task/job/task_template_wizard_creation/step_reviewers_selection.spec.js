import Vuex from "vuex";
import { shallowMount, createLocalVue } from "@vue/test-utils";
import axios from 'axios'
import step_reviewers_selection from "@/components/task/job/task_template_wizard_creation/step_reviewers_selection.vue"

const localVue = createLocalVue();
localVue.use(Vuex);

describe("step_reviewers_selection.vue", () => {
    let job;

    beforeEach(() => {
        job = {
            allow_reviews: false,
            review_chance:0 ,
            reviewer_list_ids: ['all']
          }
    })

    it("Renders component correctly if allow_reviews is false", () => {
        const wrapper = shallowMount(step_reviewers_selection, {
            localVue,
            propsData: {
              job: job
            }
          });

        expect(wrapper.html()).toContain("Would you like to enable reviews for this task?")
        expect(wrapper.html()).toContain('label="No"')
        expect(wrapper.html()).toContain('label="Yes"')
    })

    it("Renders component correctly if allow_reviews is true", () => {
        job.allow_reviews = true
        const wrapper = shallowMount(step_reviewers_selection, {
            mocks: {
                $store: {
                  state: {
                    project: {
                        current: {
                            member_list: []
                        }
                    }
                  }
                }
              },
            localVue,
            propsData: {
              job: job
            }
          });

        expect(wrapper.html()).toContain("Would you like to enable reviews for this task?")
        expect(wrapper.html()).toContain("Who is assigned to review these tasks?")
        expect(wrapper.html()).toContain("What percent of the tasks should be reviewed?")
    })

    it("Should emit next page event", () => {
        const wrapper = shallowMount(step_reviewers_selection, {
            localVue,
            propsData: {
              job: job,
              project_string_id: 'test'
            }
        });
        wrapper.vm.on_next_button_click()
        expect(wrapper.emitted().next_step).toBeTruthy()
    })
})
