import Vue from 'vue'
import 'codemirror/lib/codemirror.css'

import "codemirror/mode/shell/shell.js";
import "codemirror/addon/edit/closebrackets.js";
import "codemirror/addon/edit/trailingspace.js";
import "codemirror/addon/edit/matchbrackets.js";

import "codemirror/theme/material.css";
import "codemirror/theme/mdn-like.css";

// eslint-disable-next-line @typescript-eslint/no-var-requires
const VueCodeMirror = require('vue-codemirror');

Vue.use(VueCodeMirror, {});
