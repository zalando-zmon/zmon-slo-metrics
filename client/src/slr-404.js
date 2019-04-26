import { PolymerElement } from '@polymer/polymer/polymer-element.js';
import '@polymer/paper-button/paper-button.js';
import { html } from '@polymer/polymer/lib/utils/html-tag.js';
class Slr404 extends PolymerElement {
  static get template() {
    return html`
    <style include="common-styles">
      :host {
        display: block;
        @apply --slr-content;
        opacity: 0.66;
      }
    </style>

    <img class="icecream" src="/assets/images/icecream.png" width="150px">
    <h1>Woops! We got lost</h1>
    <p>Please follow the way back</p>
    <paper-button raised=""><a href="/product-groups" class="btn">home</a></paper-button>
`;
  }

  static get is() { return 'slr-404' }
}

window.customElements.define(Slr404.is, Slr404)
