import Vue, {createApp} from "vue";
import ImageAnnotation from "../../components/imageAnnotation/ImageAnnotation.vue";
import {UIConfig} from "./UIConfig";
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import 'vuetify/styles'
import css from 'vuetify/dist/vuetify.min.css'
import {APICredentials} from "../credentials/APICredentials";
import {DiffgramUIBase} from "./DiffgramUIBase";

export const DiffgramUI = async (hostURL: string, credentials: APICredentials, config: UIConfig): Promise<DiffgramUIBase> => {
  return new Promise((resolve, reject) => {
    const iframe = document.createElement('iframe');
    setIframeElmStyles(iframe)
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

      const vuetify = createVuetify({
        components,
        directives,
      })

      injectStyleSheets(document, iframe)
      const iframeApp = createApp(ImageAnnotation).use(vuetify).mount(wrapperIframe)
      setIframeRootStyles(iframe.contentWindow.document)
      iframe.contentWindow.document.body.appendChild(wrapperIframe)
      const uiBase = new DiffgramUIBase(iframeApp, iframe, credentials, hostURL, config.schema_id, config.directory_id)
      resolve(uiBase)
    }
  })
}


function injectStyleSheets(document: Document, iframe: HTMLIFrameElement){
  if(!iframe.contentWindow){
    return
  }
  if(!iframe.contentWindow.document){
    return
  }
  const styleElm = iframe.contentWindow.document.createElement('style')

  const head = iframe.contentWindow.document.getElementsByTagName('head')[0]
  if(!head){
    return
  }
  head.appendChild(styleElm)
  styleElm.type = 'text/css'
  styleElm.appendChild(iframe.contentWindow.document.createTextNode(css))
}

function setIframeRootStyles(iframeDocument: Document){
  const html = iframeDocument.getElementsByTagName('html')[0];
  html.style.border = 'none';
  html.style.overflow = 'hidden';
}
function setIframeElmStyles(iframe: HTMLIFrameElement){
  iframe.style.border = 'none';
}
