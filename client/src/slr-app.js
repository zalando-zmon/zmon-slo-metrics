import { PolymerElement } from '@polymer/polymer/polymer-element.js';
import '@polymer/app-route/app-location.js';
import '@polymer/app-route/app-route.js';
import '@polymer/iron-pages/iron-pages.js';
import '@polymer/app-layout/app-layout.js';
import '@polymer/paper-styles/color.js';
import '@polymer/paper-progress/paper-progress.js';
import '@polymer/paper-styles/typography.js';
import '@polymer/iron-icons/iron-icons.js';
import '@polymer/paper-tabs/paper-tabs.js';
import '@polymer/iron-media-query/iron-media-query.js';
import '@polymer/iron-flex-layout/iron-flex-layout.js';
import '@polymer/iron-ajax/iron-ajax.js';
import '@polymer/paper-menu-button/paper-menu-button.js';
import '@polymer/paper-menu-button/paper-menu-button-animations.js';
import '@polymer/paper-listbox/paper-listbox.js';
import '@polymer/paper-item/paper-item.js';
import './slr-opentracing.js';
import './slr-product-groups.js';
import './slr-products.js';
import './slr-slr.js';
import './slr-reports.js';
import './slr-notifications.js';
import './slr-search.js';
import './slr-ajax.js';
import './common-styles.js';
import { html } from '@polymer/polymer/lib/utils/html-tag.js';
import { afterNextRender } from '@polymer/polymer/lib/utils/render-status.js';
class SlrApp extends PolymerElement {
  static get template() {
    return html`
    <style include="common-styles">
      :host {
        display: block;
        --app-primary-color: var(--paper-grey-800);
        --app-secondary-color: var(--paper-grey-100);
        --app-accent-color: var(--paper-orange-400);
        --accent-color: var(--paper-orange-400);
        --app-content-max-width: 1440px;
        --slr-content: {
          max-width: var(--app-content-max-width);
          margin-left: auto;
          margin-right: auto;
          text-align: center;
        }
      }

      app-toolbar {
        @apply --paper-font-common-base;
        background-color: var(--app-primary-color);
        color: white;
        display: flex;
      }

      paper-progress {
        display: block;
        width: 100%;
        margin-top: -4px;
        --paper-progress-active-color: var(--app-accent-color);
        --paper-progress-secondary-color: var(--app-secondary-color);
      }

      .main-header {
        background-color: var(--app-primary-color);
        box-shadow: 0px 5px 6px -3px rgba(0, 0, 0, 0.4);
        margin-bottom: 20px;
      }

      .main-header[small-layout] {
        margin-bottom: 0;
      }

      .main-title {
        --app-toolbar-font-size: var(--paper-font-title);
        text-align: left;
        padding-left: 30px;
        z-index: 1;
      }

      paper-tabs {
        --paper-tabs-selection-bar-color: white;
        height: 100%;
      }

      .flex-horizontal {
        @apply --layout-horizontal;
        @apply --layout-wrap;
      }

      .flex-equal-justified {
        @apply --layout-horizontal;
        @apply --layout-justified;
      }

      .flexchild {
        @apply --layout-flex;
      }

      paper-tabs a {
        text-decoration: none;
        display: inline-block;
        pointer-events: auto;
        color: white;
        height: 20px;
        padding: 9px 5px;
      }

      paper-avatar {
        z-index: -1;
      }

      slr-search[small-layout] {
        padding: 10px;
      }

    </style>

    <slr-opentracing initialized="{{initd}}"></slr-opentracing>

    <app-location route="{{route}}"></app-location>
    <app-route route="{{route}}" pattern="/:page" data="{{routeData}}" tail="{{subroute}}"></app-route>

    <iron-media-query query="(max-width: 600px)" query-matches="{{small}}"></iron-media-query>

    <app-header reveals="" class="main-header" slot="header" hidden\$="{{headerIsHidden}}" small-layout\$="[[small]]">

      <app-toolbar class="main-title flex-horizontal flex-equal-justified">
        <div>Service Level Reporting</div>
        <div class="flexchild" hidden\$="[[small]]">
          <slr-search class="flexchild" search-str="{{searchStr}}" small-layout\$="[[small]]" hidden\$="[[searchIsHidden]]"></slr-search>
        </div>
        <paper-menu-button hidden\$="[[small]]">
          <paper-listbox slot="dropdown-content">
            <paper-item><a on-click="logout">Logout</a></paper-item>
          </paper-listbox>
        </paper-menu-button>
        <paper-menu-button hidden\$="[[!small]]">
          <paper-icon-button icon="more-vert" slot="dropdown-trigger" alt="menu"></paper-icon-button>
          <paper-listbox slot="dropdown-content">
            <paper-item on-click="openSearch">Search</paper-item>
            <paper-item><a href="/logout">Logout</a></paper-item>
          </paper-listbox>
        </paper-menu-button>
      </app-toolbar>

      <app-toolbar id="searchBar" hidden="">
        <slr-search id="searchSmall" class="flexchild" hidden\$="[[!searchIsHidden]]" search-mode="true" search-str="{{searchStr}}"></slr-search>
      </app-toolbar>

      <app-toolbar class="tabs-bar">
        <!-- Nav on desktop: tabs -->
        <paper-tabs selected="{{routeData.page}}" attr-for-selected="name">
          <paper-tab name="product-groups">
            <a href="/product-groups">Product Groups</a>
          </paper-tab>
          <paper-tab name="products">
            <a href="/products">Products</a>
          </paper-tab>
          <paper-tab name="slr">
            <a href="/slr">Reports</a>
          </paper-tab>
        </paper-tabs>
      </app-toolbar>

      <paper-progress indeterminate="" class="slow red" hidden\$="{{!loading}}"></paper-progress>
    </app-header>

    <iron-pages selected="{{routeData.page}}" attr-for-selected="name" selected-attribute="visible">

      <template is="dom-if" if="{{initd}}">

        <slr-product-groups id="productGroups" name="product-groups" route="{{subroute}}" loading="{{loading}}" product-groups="{{productGroups}}" search-str="{{searchStr}}"></slr-product-groups>

        <slr-products id="products" name="products" route="{{subroute}}" loading="{{loading}}" search-str="{{searchStr}}"></slr-products>

        <slr-slr name="slr" route="{{subroute}}"></slr-slr>

        <slr-reports name="reports"></slr-reports>

        <slr-auth name="auth"></slr-auth>

        <slr-404 name="404"></slr-404>

        <slr-error name="error"></slr-error>

      </template>

    </iron-pages>

    <slr-notifications id="notif"></slr-notifications>

    <iron-ajax id="ajax" url="/api/health" on-response="handleResponse" on-error="handleErrorResponse" handle-as="json"></iron-ajax>

    <slr-ajax auto="" id="sessionAjax" url="/api/session" handle-as="json" last-response="{{session}}"></slr-ajax>
`;
  }

  static get is() { return 'slr-app'; }

  static get properties() {
    return {
      route: {
        type: Object
      },
      subroute: {
        type: Object
      },
      routeData: {
        type: Object
      },
      initd: {
        type: Boolean,
        value: false
      },
      loading: {
        type: Boolean,
        value: false
      },
      productGroups: {
        type: Array,
        value: () => []
      },
      headerIsHidden: {
        type: Boolean,
        value: false,
        computed: 'computeHeaderIsHidden(routeData.page)'
      },
      searchIsHidden: {
        type: Boolean,
        value: false,
        computed: 'computeSearchIsHidden(routeData.page, small)'
      },
      session: {
        type: Object
      },
      small: {
        type: Boolean
      }
    }
  }

  computeSearchIsHidden(page, small) {
    if (small) {
      return true
    }
    if (page === 'product-groups' || page === 'products') {
      return false
    }
    return true
  }

  computeHeaderIsHidden(page) {
    return page === 'auth' ? true : false
  }

  static get observers() { return [
    'routePageChanged(routeData.page)'
  ]}

  routePageChanged(page) {
    if (page == null) {
      return
    }

    if (page === '') {
      return this.set('routeData.page', 'product-groups')
    }

    if (page === 'product-groups') {
      return this.pageLoaded()
    }

    // lazy loading
    let cb = this.pageLoaded.bind(this)
    let show404 = () => {
      this.show404()
    }
    import('slr-' + page + '.js').then(() => cb, show404)
  }

  ready() {
    super.ready()
    this.addEventListener('slr-authenticate', (n) => this.showAuth())
    this.addEventListener('slr-notify', (n) => this.$.notif.open(n.detail))
    this.addEventListener('slr-error', () => this.showError())
    this.$.searchSmall.addEventListener('search-closed', () => this.$.searchBar.hidden = true)
  }

  pageLoaded() {
    this.ensureLazyLoaded()
  }

  ensureLazyLoaded() {
    if (!this.loadComplete) {
      afterNextRender(this, () => {
        import('./lazy-resources.js').then(() => {
          // Register service worker if supported.
          // if ('serviceWorker' in navigator) {
          //   navigator.serviceWorker.register('service-worker.js', {scope: '/'});
          // }
          this.loadComplete = true
        })
      })
    }
  }

  show404() {
    this.set('routeData.page', '404')
  }

  showError() {
    this.set('routeData.page', 'error')
  }

  showAuth() {
    // verify if user is admin before redirecting to login page
    this.$.ajax.generateRequest()
  }

  showLogin() {
    let path = this.route.path ? `?next=${this.route.path}` : ''
    window.location.href = `/login${path}`
  }

  logout() {
    window.location.href = '/logout'
  }

  handleResponse(e) {
    if (e.detail.status === 401) {
      this.showLogin()
    }
  }

  handleErrorResponse(e) {
    if (e.detail.request.xhr.response.status === 401) {
      return this.showLogin()
    }

    this.dispatchEvent(new CustomEvent('slr-notify', {
      detail: {
        message: "Can't get server health",
        duration: 0
      },
      bubbles: true,
      composed: true
    }))
  }

  openSearch() {
    this.$.searchSmall.searchMode = true;
    this.$.searchBar.hidden = false;
  }
}

window.customElements.define(SlrApp.is, SlrApp);
