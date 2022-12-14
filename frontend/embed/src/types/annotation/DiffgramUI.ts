import {Instance} from "../instances/Instance";
import InstanceStore from "../../../../src/helpers/InstanceStore";
import {File} from "../files/File";
import Vue, {createApp} from "vue";
import ImageAnnotation from "../../components/imageAnnotation/ImageAnnotation.vue";
import App from "../../App.vue";
import {UIConfig} from "./UIConfig";
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'


export class DiffgramUIBase {
  private instanceStore: InstanceStore;
  private file: File

  private iFrame: HTMLIFrameElement

  private rootComponent: Vue.Component

  constructor(root: Vue.Component, iFrame: HTMLIFrameElement) {
    this.rootComponent = root
    this.iFrame = iFrame
  }

  public getInstanceList(): Instance[]{
    if(!this.file){
      return []
    }
    let res = this.instanceStore.get_instance_list(this.file.id)
    if (!res){
      return []
    }
    return res
  }

}

export const DiffgramUI = async (config: UIConfig): Promise<DiffgramUIBase> => {
  console.log('PROMISEE')
  return new Promise((resolve, reject) => {
    console.log('creating iframe')
    const iframe = document.createElement('iframe');
    if (iframe == null){
      reject(new Error("cannot create iframe"))
      return
    }
    const elm = document.querySelector(config.domIDSelector)
    if(!elm){
      reject(new Error(`cannot find elm ${config.domIDSelector}`))
      return
    }
    elm.appendChild(iframe)
    iframe.onload = function () {
      iframe.width = `${config.width}px`
      iframe.height = `${config.height}px`
      if(!iframe.contentWindow){
        reject(new Error(`Cannot find iframe.contentWindow`))
        return
      }
      const wrapperIframe = document.createElement("div")

      const iframeApp = createApp(ImageAnnotation).mount(wrapperIframe)

      iframe.contentWindow.document.body.appendChild(wrapperIframe)
      const uiBase = new DiffgramUIBase(iframeApp, iframe)
      resolve(uiBase)
    }
  })
}
