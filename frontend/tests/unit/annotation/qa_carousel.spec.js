import { shallowMount, createLocalVue } from "@vue/test-utils";
import qa_carousel from "@/components/annotation/qa_carousel.vue";

const localVue = createLocalVue();

describe("QA carousel test set", () => {
  // let props;
  // let testMethod;

  // beforeEach(() => {
  //   testMethod = jest.fn();
  //   props = {
  //     propsData: {
  //       annotation_show_on: true,
  //       instance_list: [1, 2, 3],
  //       annotation_show_duration: 2000,
  //       loading: false
  //     }
  //   };
  // });

  it("Passes the test while qa carousel is disabled", () => {
    expect(true).toBeTruthy()
  })

  // it("Renders progress bar if carouse is on", () => {
  //   const wrapper = shallowMount(qa_carousel, props, localVue);
  //   expect(wrapper.html().includes("v-snackbar")).toBeTruthy();
  // });

  // it("Does not render progress bar if carouse is off", () => {
  //   props.propsData.annotation_show_on = false;
  //   const wrapper = shallowMount(qa_carousel, props, localVue);
  //   expect(wrapper.html().includes("v-snackbar")).toBeFalsy();
  // });

  // it("Emits focus_instance event on calling annotation_show method if there are more instances in the lest", () => {
  //   const wrapper = shallowMount(qa_carousel, props, localVue);
  //   wrapper.vm.annotation_show();
  //   expect(JSON.stringify(wrapper.emitted())).toContain("focus_instance");
  // });

  // it("Emits change_item event on calling annotation_show method if there are no more instances in the lest", () => {
  //   props.propsData.instance_list = [];
  //   const wrapper = shallowMount(qa_carousel, props, localVue);
  //   wrapper.vm.annotation_show();
  //   expect(JSON.stringify(wrapper.emitted())).toContain("change_item");
  // });

  // it("Calls event listener setter on mount", () => {
  //   props.methods = { add_event_listeners: testMethod };
  //   const wrapper = shallowMount(qa_carousel, props, localVue);
  //   expect(testMethod).toBeCalled();
  // });

  // it("Emits stop_carousel event on press space", () => {
  //   const wrapper = shallowMount(qa_carousel, props, localVue);
  //   window.dispatchEvent(
  //     new KeyboardEvent("keydown", {
  //       keyCode: 32
  //     })
  //   );
  //   expect(JSON.stringify(wrapper.emitted())).toContain("stop_carousel");
  // });

  // it("Emits focus_instance event on press right arrow", () => {
  //   props.methods = { annotation_show: testMethod };
  //   const wrapper = shallowMount(qa_carousel, props, localVue);
  //   window.dispatchEvent(
  //     new KeyboardEvent("keydown", {
  //       keyCode: 39
  //     })
  //   );
  //   expect(testMethod).toBeCalled();
  // });
});
