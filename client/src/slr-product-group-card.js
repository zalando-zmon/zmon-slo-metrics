import { PolymerElement } from '@polymer/polymer/polymer-element.js';
import '@polymer/paper-card/paper-card.js';
import '@polymer/iron-icons/iron-icons.js';
import '@polymer/paper-button/paper-button.js';
import '@polymer/paper-icon-button/paper-icon-button.js';
import '@polymer/iron-label/iron-label.js';
import '@polymer/paper-input/paper-input.js';
import '@polymer/paper-item/paper-icon-item.js';
import '@polymer/paper-item/paper-item-body.js';
import '@polymer/iron-media-query/iron-media-query.js';
import './slr-form.js';
import { html } from '@polymer/polymer/lib/utils/html-tag.js';
class SlrProductGroupCard extends PolymerElement {
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

      paper-icon-button {
        display: inline-block;
        vertical-align: middle;
        margin: -5px;
        visibility: hidden;
      }

      paper-card:hover paper-icon-button {
        visibility: visible;

      }

    </style>

    <iron-media-query query="(max-width: 600px)" query-matches="{{smallLayout}}"></iron-media-query>

    <paper-card>
      <paper-icon-item class="card-header" hidden\$="[[editMode]]">
        <paper-item-body two-line="">
          <div>[[item.name]]</div>
          <div secondary="">[[item.department]]</div>
        </paper-item-body>
        <div class="actions">
          <paper-icon-button item-icon="" icon="delete" on-click="delete"></paper-icon-button>
          <paper-icon-button item-icon="" icon="create" on-click="toggleEditMode"></paper-icon-button>
        </div>
      </paper-icon-item>

      <div class="card-content" hidden\$="[[!editMode]]">
        <slr-form id="form" loading="{{loading}}" item="{{item}}">
          <form method="[[method]]" action="[[action]]">
            <div class="header">
              <paper-input id="name" name="name" type="text" label="Name" autofocus="true" disabled="[[!editMode]]" value="{{item.name}}" required=""></paper-input>
            </div>
            <paper-input id="department" name="department" type="text" label="Department" disabled="[[!editMode]]" value="{{item.department}}" required=""></paper-input>
            </form>
        </slr-form>
      </div>

      <div class="card-actions" hidden\$="[[!editMode]]">
        <div class="horizontal justified">
          <paper-button on-click="cancel">Cancel</paper-button>
          <paper-button on-click="submit" autofocus="">Save</paper-button>
      </div>
    

  </div></paper-card>
`;
  }

  static get is() { return 'slr-product-group-card' }

  static get properties() {
    return {
      item: {
        type: Object,
        notify: true,
        observer: 'itemChanged'
      },
      loading: {
        type: Boolean,
        value: false,
        notify: true
      },
      // save copy to reset form since iron-form
      // and paper-input have issues
      _item: {
        type: Object
      },
      editMode: {
        type: Boolean,
        value: false,
        notify: true,
        reflectToAttribute: true
      },
      method: {
        type: String,
        value: 'POST'
      },
      action: {
        type: String,
        value: '/api/product-groups',
        computed: 'computeAction(item.uri)'
      },
      deleteModalIsOpen: {
        type: Boolean,
        value: false
      },
      smallLayout: {
        type: Boolean,
        value: false,
        reflectToAttribute: true
      }
    }
  }

  ready() {
    super.ready()
    this.copyItem()
    this.$.form.addEventListener('iron-form-error', (e) => this.onError(e))
    this.$.form.addEventListener('iron-form-response', (e) => this.onResponse(e))
  }

  onError(e) {
    let method = this.$.form.request.method || 'default'
    let m = { 'POST': 'add', 'PUT': 'update', 'DELETE': 'delete', 'default': 'save' }

    try {
      if (e.detail.request.xhr.response.status === 401) {
        this.dispatchEvent(new CustomEvent('slr-authenticate', {bubbles: true, composed: true}))
      } else {
        this.notify(`Can't ${m[method]} Product Group.`,
          () => this.$.form.submit(),
          e.detail.request.xhr.response.detail)
      }
    } catch(e) {
      this.notify(`Can't ${m[method]} Product Group.`,
        () => this.$.form.submit())
    }

    this.initForm()
  }

  onResponse(e) {

    if (e.detail.response && e.detail.response.uri) {
      this.set('item.uri', e.detail.response.uri)
    }

    let method = this.$.form.request.method
    let m = {
      'POST': 'Added',
      'PUT': 'Updated',
      'DELETE': 'Deleted'
    }
    this.notify(`${m[method]} Product Group.`)

    this.dispatchEvent(new CustomEvent('product-group-submit',
      { detail: { item: e.detail.response }, bubbles: true, composed: true })
    )

    if (method === 'DELETE') {
      this.set('opened', false)
      this.set('routeData.slug', '')
    } else {
      this.set('editMode', false)
      this.set('routeData.slug', e.detail.response.slug)
      this.set('item', e.detail.response)
    }

    this.initForm()
    this.copyItem()
  }

  itemChanged() {
    if (this.item && !this.item.name) {
      this.set('editMode', true)
    }
  }

  computeAction(uri) {
    return uri ? uri : '/api/product-groups'
  }

  initForm() {
    this.set('method', 'POST')
    this.set('action', '/api/product-groups')
    this.$.form.reset()
  }

  submit() {
    if (!this.$.form.validate()) {
      return
    }
    this.$.form.submit()
  }

  delete(e) {
    this.dispatchEvent(new CustomEvent('product-group-delete',
      { detail: { item: this.item }, bubbles: true, composed: true }))
  }

  cancel() {
    this.set('editMode', false)
    this.initForm()
    this.resetItem()
    this.dispatchEvent(new CustomEvent('product-group-cancel',
      { detail: { item: this.item }, bubbles: true, composed: true })
    )
  }

  toggleEditMode() {
    this.set('editMode', !this.editMode)
    if (this.editMode) {
      this.dispatchEvent(new CustomEvent('product-group-edit',
        { detail: { item: this.item }, bubbles: true, composed: true })
      )
    }
  }

  copyItem() {
    this.set('_item', Object.assign({}, this.item))
  }

  resetItem() {
    this.set('item', Object.assign({}, this._item))
  }

  notify(message, action, detail, duration = 5000) {
    this.dispatchEvent(
      new CustomEvent('slr-notify', {
        detail: { message, action, detail, duration },
        bubbles: true,
        composed: true
      })
    )
  }
}

window.customElements.define(SlrProductGroupCard.is, SlrProductGroupCard)
