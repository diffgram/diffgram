import { shallowMount, createLocalVue } from "@vue/test-utils";
import qa_carousel from "@/components/annotation/qa_carousel.vue";

const localVue = createLocalVue();

describe("QA carousel test set", () => {
  let props;

  beforeEach(() => {
    props = {
      propsData: {
        annotation_show_on: true
      }
    };
  });

  it("Renders progress bar if carouse is on", () => {
    const wrapper = shallowMount(qa_carousel, props, localVue);
    expect(wrapper.html().includes("v-snackbar")).toBeTruthy();
  });

  it("Does not render progress bar if carouse is off", () => {
    props.propsData.annotation_show_on = false;
    const wrapper = shallowMount(qa_carousel, props, localVue);
    console.log(wrapper.html());
    expect(wrapper.html().includes("v-snackbar")).toBeFalsy();
  });
});
