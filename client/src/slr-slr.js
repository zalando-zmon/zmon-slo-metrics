import { PolymerElement } from '@polymer/polymer/polymer-element.js';
import '@polymer/app-route/app-route.js';
import { html as html$0 } from '@polymer/polymer/lib/utils/html-tag.js';
class SlrSlr extends PolymerElement {
  static get template() {
    return html$0`
    <style>
      :host {
        display: block;
        text-align: center;
      }

      iframe {
        width: 90vw;
        height: 80vh;
        background: white;
        border: none;
        margin-left: auto;
        margin-right: auto;
      }
    </style>

    <app-route route="{{route}}" pattern="/:productGroup/:product" data="{{routeData}}" tail="{{subroute}}"></app-route>

    <iframe id="iframe" src="/reports/"></iframe>
`;
  }

  static get is() { return 'slr-slr' }

  static get properties() {
    return {
      route: {
        type: Object
      },
      routeData: {
        type: Object
      },
      subroute: {
        type: Object
      },
      slug: {
        type: String,
        observer: 'slugChanged'
      }
    }
  }

  static get observers() {
    return [
      'routePathChanged(route.path)',
      'routeDataChanged(routeData.product, routeData.productGroup)'
    ]
  }

  routePathChanged(path) {
    this.setIframeSrc(path)
  }

  routeDataChanged(product, productGroup) {
    if (!this.path && (!product || !productGroup)) {
      this.setIframeSrc()
    }
  }

  setIframeSrc(path = '') {
    if (path[0] === '/') {
      path = path.slice(1)
    }
    this.$.iframe.src = '/reports/' + path
  }

  ready() {
    super.ready()
    this.$.iframe.onload = () => this.onIframeLoad()
  }

  onIframeLoad() {
    let pathname = this.$.iframe.contentWindow.location.pathname.split('/')
    let page = pathname.slice(-1)
    let path = pathname.slice(1, -1).join('/')
    // Remove '/reports/' from path, returned by navigating inside of iframe
    if (pathname.indexOf('reports') === 1) {
      path = pathname.slice(2, -1).join('/')
    }

    // set history only when slr view is visible
    if (this.route.prefix === '/slr' && path) {
      window.history.replaceState({html: page}, page, `/slr/${path}/${page}`)
    }
  }
}

window.customElements.define(SlrSlr.is, SlrSlr)
