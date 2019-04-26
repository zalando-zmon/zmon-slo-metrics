import { PolymerElement } from '@polymer/polymer/polymer-element.js';
import '@polymer/paper-fab/paper-fab.js';
import { html } from '@polymer/polymer/lib/utils/html-tag.js';
class SlrFab extends PolymerElement {
  static get template() {
    return html`
    <style>
      :host {
        display: block;
      }
    </style>

    <paper-fab icon="add" title="add"></paper-fab>
`;
  }

  static get is() { return 'slr-fab' }

  static get properties() {
    return {
      visible: {
        type: Boolean,
        reflectToAttribute: true
      }
    }
  }

  show() {
    this.set('visible', true)
  }

  hide() {
    this.set('visible', false)
  }
}

window.customElements.define(SlrFab.is, SlrFab)
