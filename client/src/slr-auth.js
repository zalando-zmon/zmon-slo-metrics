import { PolymerElement } from '@polymer/polymer/polymer-element.js';
import '@polymer/paper-button/paper-button.js';
import { html } from '@polymer/polymer/lib/utils/html-tag.js';
class SlrAuth extends PolymerElement {
  static get template() {
    return html`
    <style include="common-styles">
      :host {
        display: block;
        @apply --slr-content;
        opacity: 0.66;
      }

      h1 {
        margin-top: 15vh;
      }
    </style>

    <h1>Not logged in yet?</h1>
    <p>Please follow the authentication process</p>
    <paper-button raised="" on-click="toLogin">continue</paper-button>
`;
  }

  static get is() { return 'slr-auth' }

  toLogin() {
    window.location.href = '/login'
  }
}

window.customElements.define(SlrAuth.is, SlrAuth)
