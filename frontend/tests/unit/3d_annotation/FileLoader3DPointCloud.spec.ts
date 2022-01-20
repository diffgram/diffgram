import Vuex from "vuex";
import Vue from "vue";
import {shallowMount, createLocalVue, Wrapper} from "@vue/test-utils";
import FileLoader3DPointClouds from "../../../src/components/3d_annotation/FileLoader3DPointClouds";
import {PCDLoader} from 'three/examples/jsm/loaders/PCDLoader';
import axios from "axios";
import {mocked} from 'ts-jest/utils'
import {load} from "mime";
axios.defaults.adapter = require('axios/lib/adapters/http')

jest.mock("three/src/renderers/WebGLRenderer"); // this happens automatically with automocking
const localVue = createLocalVue();
localVue.use(Vuex);


window.alert = jest.fn();

describe("Test canvas_3d.vue", () => {
  let options;
  let wrapper: Wrapper<Vue>;
  beforeEach(() => {

  });

  it("Correctly creates a CuboidDrawerTool() object", () => {
    let ctx = {loading_pcd: false, percentage: 1}
    let loader = new FileLoader3DPointClouds(ctx);
    expect(loader.component_ctx).toMatchObject(ctx)
  });

  it("Correctly creates a load_pcd_from_url() object", async () => {
    let ctx = {loading_pcd: false, percentage: 1}
    let loader = new FileLoader3DPointClouds(ctx);
    let pcd_loader = loader.pcd_loader;


    let spy = jest.spyOn(pcd_loader, 'load')
    try{
      let mesh = await loader.load_pcd_from_url('loca.pcd') as THREE.Mesh;
    }
    catch (e) {

    }

    expect(spy).toHaveBeenCalled()
  });

});
