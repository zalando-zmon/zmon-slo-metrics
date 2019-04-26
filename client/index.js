import '/src/slr-app.js';
import '../@webcomponents/webcomponentsjs/webcomponents-loader.js';
const $_documentContainer = document.createElement('template');

$_documentContainer.innerHTML = `<title>Service Level Reporting</title><style>
      body {
        margin: 0;
        font-family: 'Roboto', 'Noto', sans-serif;
        font-size: 13px;
        line-height: 1.5;
        min-height: 100vh;
        background-color: #f5f5f5;
      }
    </style><slr-app></slr-app>`;

document.head.appendChild($_documentContainer.content);
