import { PolymerElement } from '@polymer/polymer/polymer-element.js';
import '@polymer/paper-button/paper-button.js';
import { html } from '@polymer/polymer/lib/utils/html-tag.js';
class SlrError extends PolymerElement {
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
    <h1>Something terrible happened!</h1>
    <p>We have no more Ice Cream... and this is not working. Please talk to your Administrator (about buying more Ice Cream) or...</p>
    <br>
    <paper-button raised=""><a href="/">RELOAD</a></paper-button>
`;
  }

  static get is() { return 'slr-error' }
}

window.customElements.define(SlrError.is, SlrError)
