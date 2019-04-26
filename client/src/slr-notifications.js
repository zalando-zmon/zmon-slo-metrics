import { PolymerElement } from '@polymer/polymer/polymer-element.js';
import '@polymer/iron-icon/iron-icon.js';
import '@polymer/paper-toast/paper-toast.js';
import '@polymer/paper-button/paper-button.js';
import '@polymer/paper-dialog/paper-dialog.js';
import '@polymer/paper-button/paper-button.js';
import '@polymer/paper-dialog-scrollable/paper-dialog-scrollable.js';
import './common-styles.js';
import { html } from '@polymer/polymer/lib/utils/html-tag.js';
class SlrNotifications extends PolymerElement {
  static get template() {
    return html`
    <style include="common-styles">
      :host {
        display: block;
      }

      paper-button {
        color: var(--app-accent-color);
      }

      .info {
        color: var(--app-secondary-color);
        opacity: 0.8;
        width: var(--iron-icon-width, 18px);
        height: var(--iron-icon-height, 18px);
      }
    </style>

    <paper-dialog id="detail">
      <h2>Additional Information</h2>
      <paper-dialog-scrollable>
        [[detail]]
      </paper-dialog-scrollable>
      <div class="buttons">
        <paper-button dialog-dismiss="">ok</paper-button>
      </div>
    </paper-dialog>

    <paper-toast id="toast">
      <a href="" id="more" on-click="showDetail" hidden="">
        <iron-icon class="info" icon="help-outline"></iron-icon>
      </a>
      <paper-button id="toastButton" on-click="action" hidden="">Retry</paper-button>
    </paper-toast>
`;
  }

  static get is() { return 'slr-notifications' }

  static get properties() {
    return {
      action: {
        type: Function,
        value: () => {}
      },
      detail: {
        type: String
      }
    }
  }

  open({message, action, detail, duration}) {
    this.$.more.hidden = true
    this.detail = null
    this.$.toast.close()

    if (!message) {
      console.log('Error showing notification, no message given.')
      return
    }

    this.$.toast.text = message
    this.$.toastButton.hidden = true;
    this.$.toast.duration = 3000;

    if (duration >= 0) {
      this.$.toast.duration = duration
    }

    if (action) {
      this.action = () => {
        this.$.toast.close()
        action()
      }
      this.$.toastButton.hidden = false
    }

    if (detail) {
      this.$.more.hidden = false
      this.detail = detail
    }

    this.$.toast.open()
  }

  close() {
    this.$.toast.close()
  }

  showDetail() {
    this.$.detail.open()
  }
}

window.customElements.define(SlrNotifications.is, SlrNotifications)
