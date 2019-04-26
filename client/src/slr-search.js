import { PolymerElement } from '@polymer/polymer/polymer-element.js';
import '@polymer/iron-a11y-keys-behavior/iron-a11y-keys-behavior.js';
import '@polymer/paper-input/paper-input.js';
import '@polymer/paper-icon-button/paper-icon-button.js';
import '@polymer/iron-a11y-keys/iron-a11y-keys.js';
import { html } from '@polymer/polymer/lib/utils/html-tag.js';
import { Debouncer } from '@polymer/polymer/lib/utils/debounce.js';
import { timeOut } from '@polymer/polymer/lib/utils/async.js';
class SlrSearch extends PolymerElement {
  static get template() {
    return html`
    <style>
      :host {
        display: block;
        margin-right: 10px;
      }

      .search {
        float: right;
        width: 100%;
        margin-top: -20px;
        max-width: 400px;
      }

      .searchInput {
        --paper-input-container-color: rgba(255, 255, 255, 0.3);
        --paper-input-container-focus-color: white;
        --paper-input-container-input-color: white;
      }

      .closedBtn {
        float: right;
      }
    </style>

    <iron-a11y-keys id="a11y" on-keys-pressed="onEsc" keys="esc"></iron-a11y-keys>

    <div class="search" hidden\$="{{!searchMode}}">
      <paper-input type="text" id="input" name="search" class="searchInput" placeholder="product name" autofocus="true" value="{{_searchStr}}">
        <paper-icon-button icon="search" slot="prefix"></paper-icon-button>
        <paper-icon-button icon="clear" slot="suffix" on-click="closeSearch"></paper-icon-button>
      </paper-input>
    </div>

    <div class="search-btn-container" hidden\$="{{searchMode}}">
      <paper-icon-button icon="search" class="closedBtn" on-click="onSearchClick"></paper-icon-button>
    </div>
`;
  }

  static get is() { return 'slr-search'; }

  static get properties() {
    return {
      searchMode: {
        type: Boolean,
        value: false
      },
      searchStr: {
        type: String,
        notify: true
      },
      _searchStr: {
        type: String,
        observer: '_searchStrChanged'
      }
    }
  }

  _searchStrChanged() {
    this._debounceJob = Debouncer.debounce(
      this._debounceJob,
      timeOut.after(300), () => {
        this.set('searchStr', this._searchStr)
      })
  }

  onEsc(e) {
    this.closeSearch()
  }

  onSearchClick() {
    this.set('searchMode', true)
    this.$.input.focus()
    this.dispatchEvent(new CustomEvent('search-opened'))
  }

  closeSearch() {
    this.set('_searchStr', '')
    this.set('searchMode', false)
    this.dispatchEvent(new CustomEvent('search-closed'))
  }
}

window.customElements.define(SlrSearch.is, SlrSearch)
