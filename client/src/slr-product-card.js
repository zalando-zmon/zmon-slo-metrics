import { PolymerElement } from '@polymer/polymer/polymer-element.js';
import '@polymer/paper-styles/typography.js';
import '@polymer/paper-card/paper-card.js';
import '@polymer/iron-icons/iron-icons.js';
import '@polymer/paper-icon-button/paper-icon-button.js';
import { html } from '@polymer/polymer/lib/utils/html-tag.js';
class SlrProductCard extends PolymerElement {
  static get template() {
    return html`
    <style include="common-styles">
      :host {
        display: block;
        text-align: left;
      }

      :host([edit-mode][small-layout]) {
        margin: 10px;
      }

      paper-card {
        width: 100%;
      }

      paper-card:hover .report {
        visibility: visible;
      }

      iron-icon { cursor: pointer; }

      .header {
        @apply --paper-font-headline;
        display: flex;
      }

      .title {
        flex: 2;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      .report {
        visibility: hidden;
      }

      p {
        white-space: nowrap;
        overflow: hidden;
      }
    </style>

    <paper-card>
      <div class="card-content">
        <div class="header">
          <span class="title">[[item.name]]</span>
          <a class="report" title="open report page" href="[[reportUrl]]">
            <paper-icon-button icon="assignment"></paper-icon-button>
          </a>
        </div>
        <p>[[item.product_group_name]]</p>
      </div>
    </paper-card>
`;
  }

  static get is() { return 'slr-product-card' }

  static get properties() {
    return {
      item: {
        type: Object,
        value: {}
      },
      productGroup: {
        type: Object,
        value: {}
      },
      reportUrl: {
        type: String,
        computed: 'computeReportUrl(item.slug, item.product_group_slug)'
      }
    }
  }

  computeReportUrl(slug, product_group_slug) {
    if (slug && product_group_slug) {
      return `/slr/${product_group_slug}/${slug}`
    }
  }
}

window.customElements.define(SlrProductCard.is, SlrProductCard)
