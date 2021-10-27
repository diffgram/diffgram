import Vuex from "vuex";
import { shallowMount, mount, createLocalVue } from "@vue/test-utils";
import toolbar from "@/components/annotation/toolbar.vue";

const localVue = createLocalVue();
localVue.use(Vuex);

describe("Annotation core toolbar test set", () => {
  let props;

  beforeEach(() => {
    props = {
      propsData: {
        task: 1
      },
      mocks: {
        $get_sequence_color: () => {},
        $store: {
          state: {
            user: {
              current: {
                is_super_admin: true
              }
            },
            project: {
              current: {
                project_string_id: ""
              }
            }
          },
          getters: {
            get_ui_schema: () => {}
          }
        }
      }
    };
  });

  it("Does not render change task buttons if the task is falsy", () => {
    props.propsData.task = undefined;
    const wrapper = shallowMount(toolbar, props, localVue);
    const both_buttons_are_rendered =
      !wrapper.html().includes('tooltip_message="Previous Task"') ||
      !wrapper.html().includes('tooltip_message="Next Task"');
    expect(both_buttons_are_rendered).toBeTruthy();
  });

  it("Renders change task buttons if the task is truthy", () => {
    const wrapper = shallowMount(toolbar, props, localVue);
    const both_buttons_are_rendered =
      wrapper.html().includes('tooltip_message="Previous Task"') &&
      wrapper.html().includes('tooltip_message="Next Task"');
    expect(both_buttons_are_rendered).toBeTruthy();
  });

  it("Emits event to change task to the next on click of Next Task button", async () => {
    const wrapper = shallowMount(toolbar, props, localVue);
    await wrapper
      .findAll("tooltip_button")
      .filter(w => w.attributes().tooltip_message == "Next Task")
      .at(0)
      .trigger("click");

    expect(JSON.stringify(wrapper.emitted())).toContain(
      '"change_task":[["next"]]'
    );
  });

  it("Emits event to change task to the previous on click of Previous Task button", async () => {
    const wrapper = shallowMount(toolbar, props, localVue);
    await wrapper
      .findAll("tooltip_button")
      .filter(w => w.attributes().tooltip_message == "Previous Task")
      .at(0)
      .trigger("click");

    expect(JSON.stringify(wrapper.emitted())).toContain(
      '"change_task":[["previous"]]'
    );
  });

  it("Renders play button if annotation show is off", async () => {
    const wrapper = shallowMount(toolbar, props, localVue);
    const annotation_show_button_is_rendered = wrapper
      .html()
      .includes('tooltip_message="Annotation show"');

    expect(annotation_show_button_is_rendered).toBeTruthy();
  });

  it("Does not render play button if annotation show is off", async () => {
    props.propsData.annotation_show_on = true;
    const wrapper = shallowMount(toolbar, props, localVue);
    const annotation_show_button_is_rendered = wrapper
      .html()
      .includes('tooltip_message="Annotation show"');

    expect(!annotation_show_button_is_rendered).toBeTruthy();
  });

  it("Does not render pause button if annotation show is off", () => {
    const wrapper = shallowMount(toolbar, props, localVue);
    const annotation_pause_button_is_rendered = wrapper
      .html()
      .includes('tooltip_message="Pause"');

    expect(!annotation_pause_button_is_rendered).toBeTruthy();
  });

  it("Renders pause button if annotation show is off", () => {
    props.propsData.annotation_show_on = true;
    const wrapper = shallowMount(toolbar, props, localVue);
    const annotation_pause_button_is_rendered = wrapper
      .html()
      .includes('tooltip_message="Pause"');

    expect(annotation_pause_button_is_rendered).toBeTruthy();
  });

  it("Emits annotation show event when pause button is clicked", async () => {
    props.propsData.annotation_show_on = true;
    const wrapper = shallowMount(toolbar, props, localVue);
    await wrapper
      .findAll("tooltip_button")
      .filter(w => w.attributes().tooltip_message == "Pause")
      .at(0)
      .trigger("click");

    expect(JSON.stringify(wrapper.emitted())).toContain("annotation_show");
  });
});
