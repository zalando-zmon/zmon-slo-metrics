import { PolymerElement } from '@polymer/polymer/polymer-element.js';
import '@polymer/app-route/app-location.js';
import { html } from '@polymer/polymer/lib/utils/html-tag.js';
class SlrReports extends PolymerElement {
  static get template() {
    return html`
    <style>
      :host {
        display: block;
        text-align: center;
      }
    </style>

    <app-location route="{{route}}"></app-location>

    <br><br>
    <h4>placeholder</h4>
    <p>this page is only visible on dev mode</p>
    <p>on production mode, backend redirects to reports page</p>
    <p>{{route.path}}</p>
`;
  }

  static get is() { return 'slr-reports' }
}

window.customElements.define(SlrReports.is, SlrReports)
