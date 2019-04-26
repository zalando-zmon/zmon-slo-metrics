import { PolymerElement } from '@polymer/polymer/polymer-element.js';
import '@polymer/paper-card/paper-card.js';
import '@polymer/paper-icon-button/paper-icon-button.js';
import '@polymer/paper-listbox/paper-listbox.js';
import '@polymer/paper-item/paper-item.js';
import '@polymer/paper-dropdown-menu/paper-dropdown-menu.js';
import '@polymer/paper-input/paper-input.js';
import './slr-ajax.js';
import './slr-form.js';
import { html } from '@polymer/polymer/lib/utils/html-tag.js';
class SlrTarget extends PolymerElement {
  static get template() {
    return html`
    <style include="common-styles">
      :host {
        display: block;
        margin-bottom: 15px;
      }

      .container {
        display: flex;
        flex-flow: row;
        flex-wrap: wrap;
        justify-content: flex-start;
      }

      .indicator {
        margin-right: 15px;
        vertical-align: bottom;
      }

      .from, .to {
        display: inline-flex;
        max-width: 85px;
        min-width: 60px;
        margin-right: 15px;
      }

      .actions {
        position: absolute;
        top: 5px;
        right: 5px;
      }
    </style>

    <slr-ajax id="ajax" url="[[action]]" method="[[method]]" handle-as="json" on-response="handleResponse" on-error="handleErrorResponse" content-type="application/json" debounce-duration="300" loading="{{loading}}"></slr-ajax>

    <paper-card>
      <div class="card-content">
        <slr-form id="targetForm" loading="{{loading}}" item="{{item}}">
          <form class="form">
            <div class="container">
              <div class="inputs">
                <paper-dropdown-menu label="Indicator" class="indicator" always-float-label="" disabled="{{!editMode}}" required="" noink="" no-animations="">
                  <paper-listbox id="selectList" slot="dropdown-content" selected="{{item.sli_uri}}" attr-for-selected="uri">
                    <template is="dom-repeat" items="{{indicators}}" as="indicator">
                      <paper-item uri\$="[[indicator.uri]]">[[indicator.name]]</paper-item>
                    </template>
                    <p hidden="[[indicators.length]]">No indicators found. Please add an indicator first.</p>
                  </paper-listbox>
                </paper-dropdown-menu>
                <input type="text" name="sli_uri" hidden="" value="[[item.sli_uri]]">
                <paper-input type="number" step="any" class="from" label="From" always-float-label="" disabled="[[!editMode]]" value="{{item.from}}"></paper-input>
                <paper-input type="number" step="any" class="to" label="To" always-float-label="" disabled="[[!editMode]]" value="{{item.to}}"></paper-input>
              </div>
              <slot name="actions" class="actions"></slot>
            </div>
          </form>
        </slr-form>
      </div>

    </paper-card>
`;
  }

  static get is() { return 'slr-target' }

  static get properties() {
    return {
      uri: {
        type: String,
        observer: 'uriChanged'
      },
      item: {
        type: Object,
        value: () => {}
      },
      _item: {
        type: Object,
        value: () => {}
      },
      from: {
        type: Number,
        computed: 'computeFrom(item.from)'
      },
      to: {
        type: Number,
        computed: 'computeTo(item.to)'
      },
      objective: {
        type: Object,
        value: () => {}
      },
      indicators: {
        type: Array,
        value: () => []
      },
      editMode: {
        type: Boolean,
        value: false
      },
      action: {
        type: String,
        computed: 'computedAction(uri, objective.uri)'
      },
      method: {
        type: String,
        value: 'GET'
      },
      hidden: {
        type: Boolean,
        value: false,
        reflectToAttribute: true
      },
      ignore: {
        type: Boolean,
        value: false,
        reflectToAttribute: true
      },
      loading: {
        type: Boolean,
        value: false,
        notify: true
      }
    }
  }

  uriChanged() {
    if (this.uri) {
      this.fetch()
      this.set('method', 'PUT')
    } else {
      this.set('item', {})
      this.set('method', 'POST')
    }
  }

  computeFrom(from) {
    return parseFloat(from)
  }

  computeTo(to) {
    return parseFloat(to)
  }

  computedAction(itemUri, objectiveUri) {
    return itemUri ? itemUri : objectiveUri + '/targets'
  }

  handleResponse(e) {
    this.set('item', e.detail.response)
    this.copyItem()
  }

  handleErrorResponse(e) {
    let detail = null
    let m = {
      'POST': 'add',
      'PUT': 'update',
      'DELETE': 'delete',
      'default': 'save'
    }

    try {
      detail = e.detail.request.xhr.response.detail
    } catch(e) {
      detail = "Can't parse Server response"
    }

    this.dispatchEvent(
      new CustomEvent('slr-notify', {
        detail: {
          message: `Can't ${m[this.method]} Target.`,
          action: () => this.$.ajax.generateRequest(),
          detail
        },
        bubbles: true,
        composed: true
      })
    )
  }

  fetch()  {
    this.set('method', 'GET')
    this.$.ajax.generateRequest()
  }

  validate() {
    return this.$.targetForm.validate()
  }

  submit() {
    let from = isNaN(this.from) ? null : this.from
    let to = isNaN(this.to) ? null : this.to
    this.$.ajax.body = Object.assign(this.item, { from, to })
    return this.$.ajax.generateRequest().completes
  }

  copyItem() {
    this.set('_item', Object.assign({}, this.item))
  }

  reset() {
    this.set('item', Object.assign({}, this._item))
    this.set('hidden', false)
  }
}

window.customElements.define(SlrTarget.is, SlrTarget)
