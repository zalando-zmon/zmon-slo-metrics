import { PolymerElement } from '@polymer/polymer/polymer-element.js';
import './slr-ajax.js';
import { html } from '@polymer/polymer/lib/utils/html-tag.js';
class SlrOpentracing extends PolymerElement {
  static get template() {
    return html`
    <slr-ajax auto="" sync="" url="/config.json" on-response="handleResponse" debounce-duration="300" loading="{{loading}}"></slr-ajax>
`;
  }

  static get is() { return 'slr-opentracing' }

  static get properties() {
    return {
      config: {
        type: Object,
        value: () => { return {} }
      },
      initialized: {
        type: Boolean,
        value: false,
        notify: true
      }
    }
  }

  handleResponse(e) {
    try {
      this.set('config', JSON.parse(e.detail.response))
      this.init()
    } catch(e) {
      console.error('Failed to parse Opentracing configuration', e)
    }
  }

  init() {

  }
}

window.customElements.define(SlrOpentracing.is, SlrOpentracing)
